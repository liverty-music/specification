## Context

Push notification state is currently tracked across three independent sources of truth:

1. The browser's `PushManager` subscription (physical delivery channel).
2. The backend `push_subscriptions` table row (keyed by `endpoint`, `UNIQUE`).
3. The frontend `localStorage` flag `userNotificationsEnabled`.

The backend table is already correctly keyed by browser endpoint (one row per browser session), and the repository exposes `Create` (UPSERT by endpoint), `DeleteByEndpoint`, `ListByUserIDs`, and `DeleteByUserID`. However, the RPC surface only exposes `Subscribe` and `Unsubscribe`:
- `Subscribe` writes to the DB.
- `Unsubscribe` calls `DeleteByUserID`, removing every browser's subscription at once — inconsistent with the per-endpoint schema design.
- No read RPC exists, so the frontend cannot query backend state.

To compensate, the frontend uses a `localStorage` flag as its own cache. The settings toggle is rendered from `storedPref && notificationManager.permission === 'granted'`. Every enable path (`settings-route`, `PostSignupDialog`, `NotificationPrompt`) must remember to write the flag; `PostSignupDialog` and `NotificationPrompt` forget, producing the OFF-after-enable bug.

The root fix is to make the backend DB the single source of truth, expose a read RPC, drop the `localStorage` flag, and have the settings page self-heal stale rows on load.

## Goals / Non-Goals

**Goals:**
- Eliminate the three-way divergence by reducing sources of truth to two (browser `PushManager` + backend DB), with the DB as authoritative.
- Introduce a read RPC so the settings toggle derives its state from backend truth instead of a local cache.
- Fix the OFF-after-enable bug structurally — no code path relies on remembering to write a flag.
- Align RPC naming with the repository layer and AIP Standard Methods (`Create`/`Get`/`Delete`).
- Elevate push subscription materials to first-class entity types (`PushSubscription`, `PushEndpoint`, `PushKeys`) instead of ad-hoc fields inside the request message.

**Non-Goals:**
- Multi-device UI ("show me all my devices and let me disable them individually"). The toggle is explicitly scoped to "this browser" only. Device management is a future change.
- Migrating existing orphan DB rows proactively. Existing `410 Gone` cleanup in `PushNotificationUC.NotifyNewConcerts` is sufficient.
- Unifying the authentication pattern for other services. That is a separate change (`standardize-user-scoped-rpc-auth`).

## Decisions

### D1: Backend DB is the single source of truth; `localStorage` flag is removed

**Decision:** Remove `StorageKeys.userNotificationsEnabled`. The settings toggle is computed from (a) the presence of a browser `PushSubscription` object and (b) the result of `PushNotificationService.Get(user_id, endpoint)`.

**Rationale:** The cache compensates for a missing read path. Once the read path exists, the cache becomes a liability — every writer must remember to update it, and it cannot represent cross-device state. Removing it restructures the bug out of existence.

**Alternatives considered:**
- *Move the `localStorage` write into `PushService.subscribe()` so callers cannot forget.* Fixes the immediate bug but keeps three sources of truth and does not enable multi-device reasoning.
- *Derive the toggle solely from `PushManager.getSubscription()`.* Simpler, but diverges from the backend when the browser has a subscription that was never successfully registered server-side — exactly the orphan case that self-heal must handle.

### D2: `Get` returns `NOT_FOUND` when the subscription does not exist

**Decision:** `GetPushSubscription` returns `NOT_FOUND` instead of an empty response when no row matches `(user_id, endpoint)`.

**Rationale:** AIP-131 (Standard Get) prescribes `NOT_FOUND` for absent resources. An absent-but-OK response forces clients to branch on "error or null subscription?" — two code paths for one outcome. With `NOT_FOUND`, the self-heal flow is a clean `try { get } catch (NotFound) { create }`.

**Alternatives considered:**
- *Return an empty `GetPushSubscriptionResponse` when not found.* Conflicts with AIP-131 and complicates client logic.

### D3: `Delete` takes `(user_id, endpoint)`, not just the caller's identity

**Decision:** `DeletePushSubscriptionRequest` carries both `user_id` and `endpoint`. The handler deletes only the row matching this pair.

**Rationale:** The schema is already per-endpoint. Deleting all of a user's subscriptions on an "Unsubscribe" click is surprising behavior — users expect the toggle to affect the device they are currently using, not every device they have ever signed in from. This also lets multi-device UI (future work) layer on top without another breaking change.

**Alternatives considered:**
- *Keep `Unsubscribe` deleting all rows.* Matches current behavior but contradicts the schema and blocks multi-device UX.

### D4: Self-healing for browser-has-subscription-but-DB-missing

**Decision:** On settings page load, if the browser has a `PushSubscription` and `Get` returns `NOT_FOUND`, the frontend calls `Create` with the browser's existing subscription material and sets the toggle to ON.

**Rationale:** The browser's subscription represents intent ("I want notifications"). If the DB lost the row (failed RPC, another browser's Delete, etc.), the correct UX is silent recovery — the user already granted browser permission, so no additional prompt is needed.

**Alternatives considered:**
- *Show the toggle as OFF and require the user to re-enable manually.* Safer but treats a recoverable state as user-visible error.
- *Always call `Create` on every load regardless of `Get` result.* Unnecessary writes; `Create` is UPSERT so it is safe but wasteful.

### D5: Entity types for push subscription materials

**Decision:** Introduce `entity/v1/push_subscription.proto` with `PushSubscriptionId` (UUID wrapper), `PushEndpoint` (URI wrapper), `PushKeys` (p256dh + auth pair), and `PushSubscription` aggregate. `SubscribeRequest`-style ad-hoc fields are removed.

**Rationale:** Matches the repo's existing convention (`UserId`, `ArtistId`, etc.) for type-safe IDs and domain wrappers. Makes the RPC surface symmetric — `Get` returns a `PushSubscription` entity rather than re-shaping the fields into a different response message.

**Alternatives considered:**
- *Keep the primitives inline in request/response messages.* Inconsistent with the rest of the entity layer.

### D6: RPC naming aligns with repository and AIP

**Decision:** `Subscribe` → `Create`, `Unsubscribe` → `Delete`, new `Get`. The service name `PushNotificationService` is unchanged.

**Rationale:** AIP-132/131/135 Standard Methods. The repository already uses `Create`/`Delete`/`Get`, so proto ↔ Go symmetry eliminates a translation layer.

**Alternatives considered:**
- *Keep `Subscribe`/`Unsubscribe` as domain verbs.* More readable in isolation, but forces every maintainer to mentally map `Subscribe ≡ Create`.

### D7: Repository surface simplification

**Decision:** Drop `DeleteByEndpoint(endpoint)` and `DeleteByUserID(userID)`. Replace with `Get(userID, endpoint)` and `Delete(userID, endpoint)`. Keep `Create` and `ListByUserIDs` (the latter is internal-only for push delivery).

**Rationale:** Every authenticated operation should be scoped to the caller. `DeleteByEndpoint` alone allowed deleting another user's row if the endpoint were leaked; `DeleteByUserID` enabled the "delete everything" RPC that is being retired. The new pair matches the RPC surface exactly.

**Alternatives considered:**
- *Keep `DeleteByEndpoint` for internal cleanup (`410 Gone`).* The cleanup path already knows the `user_id` (via `ListByUserIDs`), so scoping is trivial.

## Risks / Trade-offs

- **Risk:** Existing users in state "browser has subscription, DB has row, localStorage has `'false'` (or missing)" — on first load after deploy, the self-heal flow runs and corrects the UI. → Mitigation: analyzed in Open Questions below; no explicit migration needed.
- **Risk:** `Create` is called unnecessarily often if the self-heal branch triggers frequently. → Mitigation: self-heal only runs when `Get` returns `NOT_FOUND`, which should be rare in steady state.
- **Risk:** Orphan DB rows (browser data cleared) accumulate until the next push attempt triggers `410 Gone` cleanup. → Mitigation: existing behavior; impact is minimal since the endpoints are dead. Optional future enhancement: periodic backend sweep.
- **Trade-off:** Breaking proto change requires specification PR → Release → BSR gen → backend/frontend PRs (standard workspace cross-repo order). → Mitigation: documented in proposal; backend/frontend PRs can be drafted early and will pass CI once BSR gen completes.
- **Trade-off:** The RPC now requires the client to send its own `user_id` (matching the pattern used by `standardize-user-scoped-rpc-auth`). Deeper defense against client bugs at the cost of a slightly more verbose request shape.

## Migration Plan

1. Merge specification PR; publish Release; BSR gen completes.
2. Merge backend PR. Old `Subscribe`/`Unsubscribe` handlers are removed; new `Create`/`Get`/`Delete` are available. Clients using old proto will hit `UNIMPLEMENTED` — acceptable because frontend deploys immediately after.
3. Merge frontend PR. On first load after deploy, the settings page executes the self-heal flow for each existing user. No server-side migration job is needed.

**Rollback:** Revert in reverse order (frontend → backend → specification). Frontend revert restores the `localStorage`-based behavior; backend revert restores the old RPC. Because proto types change, a partial rollback (e.g., frontend only) will fail — must revert as a set.

## Open Questions

- Does the existing `ListByUserIDs` use in `PushNotificationUC.NotifyNewConcerts` rely on batch semantics for any reason beyond efficiency? If yes, confirm that scoping cleanup by `(user_id, endpoint)` rather than endpoint-only still fits that flow. (Expected answer: yes, the user_id is known at cleanup time because `ListByUserIDs` returned it alongside the endpoint.)
- The migration analysis identifies state D (browser empty, DB has row, localStorage has stale value) as benign. Confirm the product team is comfortable with orphan rows persisting until the next push-delivery-triggered cleanup. (Expected answer: yes — invisible to the user, harmless to the system.)
