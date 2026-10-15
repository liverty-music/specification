## Context

See proposal.md - Why. The approved plan is `~/.cache/referral-attribution-plan/plan.html`; the owner's decisions of 2026-10-15 override it where they differ (the 7-day device period, same-Series only, last link wins, a new table, protovalidate on the code). Current state, verified on 2026-10-15 (backend `main` adc8c33, frontend `main` e4b21fb, specification `main` 0106b7db, proto v0.85.0):

- **Fan event page.** `loading()` reads only `params.id` (frontend `src/routes/event/event-route.ts:79-83`); the fan app reads no query parameter except `devPreview` (`src/routes/welcome/welcome-route.ts:275`). The buy and entry actions are plain links, `/events/<id>/checkout` and `/events/<id>/lottery/<ticketTypeId>` (`event-route.ts:297-307`). A guest's sign-up passes `returnTo: '/events/<id>'` without the query in the OIDC state (`event-route.ts:432-437`, `shared/services/auth-service.ts:328-342`). The event's Series id is on the loaded event (`src/routes/event/event-page.ts:22,50`).
- **Link preview and share.** og:url is built on the server from the path only (`index.html:29`, `Caddyfile:12-47`); the share control uses `canonicalEventUrl` without the query (`event-page.ts:172-174`). Neither changes.
- **Start requests.** `CheckoutService.Start` and `LotteryEntryService.Start` carry `ticket_type_id = 1` and `ticket_count = 2` (`proto/liverty_music/rpc/checkout/v1/checkout_service.proto:130-140`, `rpc/lottery_entry/v1/lottery_entry_service.proto:136-147`). The fan app calls them at `src/routes/checkout/checkout-route.ts:397-401` and `src/routes/lottery-entry/lottery-entry-route.ts:282-286`; both routes have `this.event.seriesId` loaded before (`checkout-route.ts:168-173`, `lottery-entry-route.ts:141-146`).
- **Start usecases.** `checkoutUseCase.Start` ends with `checkoutRepo.GetOrCreateHeld` (backend `internal/usecase/checkout_uc.go:116-143`); `lotteryEntryUseCase.Start` ends with `entryRepo.GetOrCreateDraft` (`internal/usecase/lottery_entry_uc.go:196-237`). A count change makes a new Checkout or Draft and ends the old one (`entity/checkout/get-or-create-held`, `entity/lottery-entry/get-or-create-draft`).
- **Orders.** `orders` names its source with `checkout_id` or `lottery_entry_id` (`chk_orders_one_source`), and `status` 1 is Paid (`internal/infrastructure/database/rdb/schema/schema.sql:855-877`). Orders are created by Confirm, the payment webhook and the issuance sweepers; none of them changes here.
- **Organizer read.** `ticketSaleUseCase.ListOwnByEvent` returns `[]*TicketSaleView` with per-TicketType lottery stats (`internal/usecase/ticket_sale_uc.go:361-390`); the response carries `LotteryEntryStats` beside the sales (`rpc/organizer/ticket_sale/v1/ticket_sale_service.proto:191-232`). The Sales tab reads it at `organizer/event/sales-tab/sales-tab.ts:116-130` through `organizer/services/ticket-sale-client.ts:80-98`.
- **Database roles.** `organizer-console-api` keeps SELECT and the SELECT default privilege on every app table and only a listed write set (`k8s/atlas/base/migrations/20261008020000_restrict_organizer_console_api_and_zitadel_app_grants.sql`); `fan-api`, `backend-app`, `admin-console-api` keep full CRUD; `reception-api` has nothing outside its list. `rdb.TestMigrationGrants_IAMRoles` checks every app table, new ones included (`internal/infrastructure/database/rdb/migration_grants_integration_test.go:119-229`). The newest migration is `20261013002947_migrate_discovered_sales.sql`.
- **Privacy Policy.** The text is in `src/locales/{ja,en}/translation.json` under `legal.privacy` (from line 591). Section 2 (lines 605-614) lists account information, wallet address, home area, follows, language, push subscription and analytics data. It lists no purchase data (no orders, tickets, name or phone) and no Stripe; `payments-legal-compliance` task 3.2 adds only the Stripe cross-border disclosure.
- **PostHog.** Autocapture and pageviews are off (`src/lib/analytics/analytics-service.ts:352-355`); nothing reads or strips `ref`. Inferred, not verified: posthog-js attaches `$current_url` with the query to the custom events it sends, so a `ref` value can reach PostHog as part of a URL. This change does not use it.

## Goals / Non-Goals

**Goals:**
- Attribute each Paid Order to the referral code its Checkout or LotteryEntry started with, without touching the Order issuance paths or the existing tables.
- Show the counts per code on the Sales tab with the existing organizer read.
- Remove the undefined prefix `liverty` from client-side storage names in the same frontend release.

**Non-Goals:**
- Code registration, a code management screen, reward payouts, per-code reports outside one event, CSV export.
- Attribution across devices, or by a fan's account: the code lives on the device that opened the link.
- A PostHog event or funnel for referrals. (D11 only removes query strings from what PostHog already receives.)
- Stopping a modified client from sending any code: the server checks only the format (D2).

## Decisions

### D1 — A Referral belongs to the Checkout or LotteryEntry, in its own table

`Referral` names its source (a Checkout or a LotteryEntry) and holds the code. The table `referrals`:

| column | type | rule |
|---|---|---|
| `id` | UUID | primary key, UUIDv7 (`chk_referrals_id_uuidv7`) |
| `checkout_id` | UUID NULL | `REFERENCES checkouts(id) ON DELETE CASCADE`; unique where not null |
| `lottery_entry_id` | UUID NULL | `REFERENCES lottery_entries(id) ON DELETE CASCADE`; unique where not null |
| `code` | TEXT | `chk_referrals_code`: `code ~ '^[a-z0-9-]{1,32}$'` |
| `create_at` | TIMESTAMPTZ | not null |

`chk_referrals_one_source` requires exactly one of the two source columns, mirroring `chk_orders_one_source`. `ON DELETE CASCADE` realizes "A Referral lives with its source": `Concert.DeleteAndSuppress` (`rdb/concert_repo.go:271`) and `Organizer.Delete` (`rdb/organizer_repo.go:412`) delete Checkouts, and `lottery_entries` cascade from `ticket_types`; none of those statements changes. Purchases without a code get no row.

- **Why the source, not the Order:** the code is known at Start, before any Order exists, and Orders are created in four places (Confirm, the payment webhook, two sweepers). Recording on the source keeps all four unchanged; the stats reach the code through `orders.checkout_id` / `orders.lottery_entry_id`.
- **Rejected — a `referral_code` column on `checkouts`, `lottery_entries` or `orders`** (owner, 2026-10-15): few purchases will carry a code, so the column would be mostly empty, and a column on `orders` would need every issuance path to copy it.
- **Rejected — the name `Attribution`:** an advertising term with a wider meaning. A Referral is "one purchase brought by a link".

### D2 — `ReferralCode`: free-form, format checked at the boundary and in the entity

- Proto: a new `entity/v1/referral.proto` with `message ReferralCode { string value = 1 [(buf.validate.field).string = {min_len: 1, max_len: 32, pattern: "^[a-z0-9-]+$"}]; }`. No `Referral` message: no RPC returns a Referral (rpc-design: messages exist for what the API carries).
- Go: `entity.ReferralCode` (string) with `Validate()` using the same rule; the DB CHECK repeats it.
- The server checks only the format; whether the code belongs to the event's Series is the fan app's rule (D7). A modified client can therefore record any well-formed code. That is acceptable because a code grants nothing and pays nothing.
- **Codes are lowercase** (spec `entity/referral` "Referral code format"; owner decision 2026-10-15, was Assumption A1). The fan app lowercases `?ref=` before it validates and keeps it, so `Member-A` and `member-a` count as one code. The proto pattern and the DB CHECK accept lowercase only; an uppercase code from any other client fails InvalidArgument.

### D3 — `Referral.Record` on `ReferralRepository`, called by Start

- `entity.ReferralRepository` in `internal/entity/referral.go`:
  - `Record(ctx, source ReferralSource, code ReferralCode, at time.Time) error`, where `ReferralSource` holds exactly one of `CheckoutID` and `LotteryEntryID`;
  - `ListStatsByEvent(ctx, eventID string) ([]ReferralCodeStats, error)` (D4).
- Realized by `rdb.ReferralRepository`. `Record` runs one transaction:
  1. `SELECT status FROM checkouts WHERE id = $1 FOR SHARE` (or `state` from `lottery_entries`); no row → FailedPrecondition.
  2. Not open (Checkout not Held, entry not Draft) → commit and return nil.
  3. `INSERT … ON CONFLICT (checkout_id) WHERE checkout_id IS NOT NULL DO UPDATE SET code = EXCLUDED.code WHERE referrals.code <> EXCLUDED.code` (same for `lottery_entry_id`).

  The row lock serializes Record with `Checkout.Commit` and `LotteryEntry` confirmation, which update the same row, so a code cannot change after the source is confirmed. A plain conditional upsert is not enough under READ COMMITTED: it could read Held, then write after a concurrent commit.
- `CheckoutUseCase.Start` and `LotteryEntryUseCase.Start` take `code *entity.ReferralCode` (nil = no code) and call `referralRepo.Record` after `GetOrCreateHeld` / `GetOrCreateDraft` returns.
- **A Record failure fails Start** (Assumption A2). The hold or Draft stays, and a retry resumes it and records again, so nothing is lost. **Rejected — log and continue:** it hides a broken write from the fan and the Organizer, and the database is the same one that just served `GetOrCreateHeld`, so a failure here means the request is failing anyway.
- **A count change** releases the old Checkout (or withdraws the old Draft) and returns a new one. The new one gets the code the app sends; the old one's Referral stays and is never counted, because no Order is made from it.

### D4 — The stats are an entity operation, not an entity

`Referral.ListStatsByEvent` returns `[]entity.ReferralCodeStats{Code *ReferralCode; OrderCount, TicketCount int; Amount int64}`, `Code == nil` for the direct group.

- **Why not an entity** (owner's question): the stats have no identity, no lifecycle and no stored row of their own. They are computed from Orders and Referrals each time they are read, like `LotteryEntry.GetStatsByTicketType` (`entity/lottery-entry/get-stats-by-ticket-type`). An entity would need stored counters that the Order issuance and refund paths keep up to date, which D1 avoids.
- **Why on Referral:** the result is grouped by the Referral's code. An operation on Order would read as "Orders by something" and hide that the code is the key.
- One query in `rdb.ReferralRepository`:
  ```sql
  SELECT r.code, count(*), sum(coalesce(c.ticket_count, le.ticket_count)), sum(o.amount)
  FROM orders o
  LEFT JOIN checkouts c        ON c.id = o.checkout_id
  LEFT JOIN lottery_entries le ON le.id = o.lottery_entry_id
  JOIN ticket_types tt         ON tt.id = coalesce(c.ticket_type_id, le.ticket_type_id)
  LEFT JOIN referrals r        ON r.checkout_id = o.checkout_id OR r.lottery_entry_id = o.lottery_entry_id
  WHERE tt.event_id = $1 AND o.status = 1  -- Paid
  GROUP BY r.code
  ORDER BY count(*) DESC, r.code COLLATE "C"
  ```
  `COLLATE "C"` gives the character-by-character order of the spec. The query starts from `idx_ticket_types_event_id`; `uq_orders_checkout_id`, `uq_orders_lottery_entry_id` and the unique source indexes of D1 serve the joins; an event has at most a few thousand Orders.
- Tickets are the source's ticket count, not the Order's live Tickets, so a later resale void does not change who sold the ticket.
- Lottery entries count only through their Order: an Entered or Lost entry has no Order. That answers the brief's question: a lottery win counts once Won and charged.

### D5 — RPC surface

Following the rpc-design skill (`.claude/skills/rpc-design/SKILL.md`): no new service, because no RPC acts on a Referral by itself; the field names repeat across both Start requests ("Request fields with the same meaning have the same name across services").

- Fan `CheckoutService.StartRequest` and `LotteryEntryService.StartRequest`: `optional entity.v1.ReferralCode referral_code = 3;`. protovalidate rejects a malformed code with InvalidArgument before any usecase (specs `adapter/fan/api/rpc/{checkout,lottery-entry}`). The handlers map it to `*entity.ReferralCode`.
- Organizer `TicketSaleService.ListByEventResponse`: `repeated ReferralCodeStats referral_code_stats = 3;` with, in the same RPC file next to `LotteryEntryStats` (precedent: a read-only tally that only this response carries):
  ```proto
  message ReferralCodeStats {
    optional entity.v1.ReferralCode code = 1; // absent: purchases without a code (direct)
    int32 order_count = 2 [(buf.validate.field).int32.gte = 0];
    int32 ticket_count = 3 [(buf.validate.field).int32.gte = 0];
    int64 amount = 4 [(buf.validate.field).int64.gte = 0]; // whole yen, 税込
  }
  ```
- `TicketSaleUseCase.ListOwnByEvent` returns `*OwnEventSales{Sales []*TicketSaleView; ReferralCodeStats []entity.ReferralCodeStats}` instead of the bare slice. It calls `Referral.ListStatsByEvent` after the ownership check.
- All additions; one minor proto release (v0.86.0 expected), no `buf skip breaking`.

### D6 — Migration and database roles

- One Atlas migration after `20261013002947`, creating `referrals` (D1), plus the same table in `rdb/schema/schema.sql` and a `COMMENT ON TABLE`.
- **No grant is written.** The organizer server only reads `referrals` (D4), and the SELECT default privilege from 20261008020000 covers a new table. `fan-api` writes it through its full-CRUD default. `reception-api` gets nothing, as before.
- `TestMigrationGrants_IAMRoles` already loops over every app table. It proves `referrals` is SELECT-only for `organizer-console-api`, invisible to `reception-api` and full CRUD for `fan-api`. The test needs no change; running it is the check (task 3.1).
- **cloud-provisioning:** no change. No new role, secret or service.

### D7 — The fan app keeps the code on the device

- New `src/adapter/storage/referral-storage.ts`, in the pattern of `checkout-storage.ts` (module functions, every access in try/catch). It holds the localStorage key `referral` with value `{"code": "...", "seriesId": "...", "expiresAt": <epoch ms>}`. `load()` returns null and removes the entry when it is malformed or expired.
  - **Why localStorage:** it survives the OIDC round trip, other tabs and closing the browser. sessionStorage would lose the code in a new tab, and the sign-up return path cannot carry it (decision 3: the path stays as it is).
  - **Sign-out does not clear it.** It is not personal data of the account, and the sign-out cleanup removes only named keys and the `guestMerged:` prefix (`src/services/follow-store.ts:463`).
- Capture: in `event-route.ts`, after the event loads, read `ref` from `window.location.search`. Lowercase it; when it matches `^[a-z0-9-]{1,32}$`, save it with `this.event.seriesId` and `Date.now() + 7 days`. The address bar keeps `?ref=`, and nothing else on the page changes.
- Send: the checkout and lottery entry routes load the kept code just before Start. They pass it only when `seriesId === this.event.seriesId`, through a new optional argument of `checkoutClient.start` / `entryClient.start`.
- The code stays after a purchase, so a second purchase within 7 days of the same Series counts for the same link (Assumption A5).
- **Rejected — the Series check on the server:** it would need the Series on the request or in a server-side session. The owner placed this rule in the app (decision 4), and a stray code has no effect beyond the count.

### D8 — The organizer Sales tab

- `EventTicketSales` (`organizer/services/ticket-sale-client.ts:42-45`) gains `referralCodeStats`. `organizer/model/sale-model.ts` maps it to rows: the code as given, `件`, `枚`, and the yen amount formatted like the sale prices. The direct row is moved last.
- `sales-tab.html` renders the section after the sales list (`</ul>` at line 97) inside the `ready` state, as a table with a caption, a short note on what counts, and `まだ購入はありません` when there are no rows. ja and en strings go under `sale.referral.*` in the organizer locales.
- The section appears only when the event has at least one sale (Assumption A4).

### D9 — Storage names without `liverty`

Every client-side storage name drops the prefix (owner, 2026-10-15). Names follow the style the unprefixed keys already use: `<area>.<name>`, plus `:<id>` for a per-id key (`guest.home`, `ui.sessionCount`). Inventory from frontend `main` e4b21fb:

| kind | old | new | where |
|---|---|---|---|
| localStorage | `liverty:postSignup:shown` | `postSignup.shown` | `src/constants/storage-keys.ts:6` |
| localStorage | `liverty:sound:muted`, `liverty:sound:volume` | `sound.muted`, `sound.volume` | `storage-keys.ts:16-17` |
| localStorage | `liverty:beams:enabled` | `beams.enabled` | `storage-keys.ts:19` |
| localStorage | `liverty:fab:handed` | `fab.handed` | `storage-keys.ts:22` |
| localStorage | `liverty:guestMerged:<userId>` | `guestMerged:<userId>` | `storage-keys.ts:69` |
| localStorage | `liverty:consent:state:v2` | `consent.state` | `src/adapter/storage/consent-storage.ts:15` |
| localStorage | `liverty:analytics:noticeSeen` | `analytics.noticeSeen` | `src/routes/consent/consent-route.ts:20` |
| localStorage | `liverty:onboarding:helpSeen:<page>` | `onboarding.helpSeen:<page>` | `src/adapter/storage/onboarding-storage.ts:6` |
| localStorage | `liverty:checkout:<eventId>` | `checkout:<eventId>` | `src/adapter/storage/checkout-storage.ts:11` |
| localStorage | `liverty:verify:sessionId` | `verify.sessionId` | `src/adapter/storage/verify-session-storage.ts:23` |
| localStorage | `liverty:organizer:org_id` | `organizer.orgId` | `organizer/services/org-handle.ts:23` |
| localStorage | `liverty:organizer:last-artist:<organizerId>` | `organizer.lastArtist:<organizerId>` | `organizer/adapter/storage/last-artist-storage.ts:12` |
| sessionStorage | `liverty:lang:backfillAttempted` | `lang.backfillAttempted` | `storage-keys.ts:41` |
| sessionStorage | `liverty:follow:reconcileAttempted` | `follow.reconcileAttempted` | `storage-keys.ts:47` |
| sessionStorage | `liverty:pwaBanner:dismissed` | `pwaBanner.dismissed` | `storage-keys.ts:52` |
| sessionStorage | `liverty:auth:returnTo` | `auth.returnTo` | `shared/services/auth-service.ts:134` |
| sessionStorage | `liverty:organizer:callback-retry` | `organizer.callbackRetry` | `organizer/auth-callback/auth-callback-route.ts:20` |
| sessionStorage | `liverty:organizer:org-mismatch-retry` | `organizer.orgMismatchRetry` | `organizer/hooks/org-enforcement.ts:11` |
| IndexedDB | `liverty-wallet` | `wallet` | `src/adapter/storage/wallet-storage.ts:38-43` |
| IndexedDB | `liverty-reception` | `scanner` | `reception/services/scanner-key-store.ts:22-24` |
| IndexedDB | `liverty-analytics` | `analytics` | `src/lib/analytics/notification-interaction.ts:113-114` |
| Cache Storage | `liverty-config-offline` | `config-offline` | `src/lib/offline/offline-fallback.ts:9` |
| Cache Storage | `liverty-runtime-config` | `runtime-config` | `src/lib/push/push-renewal.ts:29` |
| Cache Storage | `liverty-analytics-identity-v1`, URL `/__liverty__/analytics-identity` | `analytics-identity`, URL `/__analytics__/identity` | `notification-interaction.ts:65,70` |
| notification tag | `liverty-default` | `default` | `src/sw.ts:120` |
| postMessage type | `liverty:push:subscription-changed` | `push.subscriptionChanged` | `src/lib/push/push-renewal.ts:25-26`, `src/main.ts:341` |

The postMessage type is not storage. It is in the list because it is the last client-side name with the prefix, and renaming it costs one constant.

**Deleted, not renamed** (no users): `liverty:consent:state:v1` and `liverty:consent:deferred:v1` with `migrateFromV1()` (`consent-storage.ts:22-23,98-100,115-150`); `migrateStorageKeys()` with `liverty:userId:<sub>` and the unprefixed legacy keys `guest.adminArea`, `user.adminArea`, `pwa.sessionCount`, `pwa.installPromptDismissed`, `pwa.completedSessionCount`, `guest.language` (`storage-keys.ts:79-120`); the `onboardingStep` migration (`onboarding-storage.ts:5,42-48`). The comment at `scanner-key-store.ts:18-21`, which says the database must not be renamed, is replaced by a pointer to this decision.

**Verified consequence for devices that already hold data:**
- **Fan WalletPublicKey.** The renamed `wallet` database starts empty. The app registers a new key on its own only when the server has none. When the server already has one, the tickets screen shows that the entry QR code is set up on another device and offers この端末で入場する. A new key is registered only after the fan confirms (`src/services/ticket-wallet.ts:84-126`; spec `route/tickets` "The entry device is chosen once and moves only when the fan asks"). `WalletPublicKeyService.Register` replaces the stored key (`rdb/wallet_public_key_repo.go:31-40`). Offline, the screen shows `needs-connection` until the fan goes online (`ticket-wallet.ts:228-239`). So no regeneration code is missing: the owner and the tester tap この端末で入場する once on each phone. Signing out already empties this database (`ticket-wallet.ts:75,160-167`), so this is the same state as after a sign-out.
- **Scanner.** The renamed `scanner` database starts empty. The reception page makes a new key pair, and `ScannerService.Open` answers FailedPrecondition, which the page shows as "in use on another device; ask for a reissue" (`reception/scanner-route/scanner-route.ts:263-275`; backend `usecase/scanner_uc.go:217-252`; spec `usecase/scanner/open` "Link forwarded to another device"). The only remedy is 取り消して再発行 on the event's Reception tab, which issues a new Scanner with a new number and link (spec `route/event` "Revoke and reissue a Scanner"). Task 6.4 checks production for InUse Scanners of events that have not ended, and reissues them after the deploy.
- **Other renamed names** lose their values once: the consent choice is asked again, page help opens again, the beam, sound and hand preferences reset, and the id of an open checkout is forgotten. The old entries and caches stay on the device unused. No cleanup code is added, because only two devices are affected (Assumption A7).
- **Specs that name keys** (`global/post-signup-dialog`, `global/page-help`, `global/fab-menu`, `stories/merge-guest-data-on-signup`) get MODIFIED blocks with the new names. `route/my-artists` and the story still mention `liverty:guest:hypes`, which no code writes. The deltas drop it, and the my-artists scenario now names the follow entry that actually holds the hype. No doc in `specification/docs` or in the frontend `docs/`, `AGENTS.md` or `README.md` names these keys.

### D10 — Privacy Policy text

Add to section 2 of `legal.privacy` in ja and en:
- ・購入に関する情報（注文、チケット、本人確認のための氏名・電話番号、決済の参照番号）
- ・購入の経路（紹介リンクに含まれる紹介コード）

Add to section 3 (purposes): measuring which links led to purchases and reporting the count per code to the Organizer of the event. Update the revision date. The spec `global/legal-document` enumerates the categories, so its scenario is MODIFIED. The purchase-records line fills an existing gap; the plan's mockup already shows it (Assumption A3). The Stripe cross-border wording stays with `payments-legal-compliance` task 3.2.

### D11 — Analytics events carry no query of the app's own URLs

- Verified (PostHog docs, 2026-10-15): posthog-js attaches `$current_url` (with its query) to every captured event, and `before_send` is the documented hook to rewrite an event before it is sent (https://posthog.com/docs/privacy/data-collection, https://posthog.com/docs/libraries/js/usage). The fan app sets no `before_send` today (`src/lib/analytics/analytics-service.ts:342-366`). Only the fan app sends to PostHog; the organizer and reception apps do not.
- Inferred, not verified: the SDK also records first-visit URL properties (`$initial_current_url`, `$session_entry_url`) on the person; the rule below covers them by matching on value, not on a fixed key list.
- Add `before_send` to `initConfig`: walk `properties`, `$set` and `$set_once` and, for every string value that parses as a URL on `window.location.origin`, drop its `search` and `hash`. Values on other origins (an external `$referrer`) stay as they are. Pure function in `src/lib/analytics/strip-own-url-query.ts`, unit-tested on its own.
- **Why now:** codes are free-form, so a promoter can choose a person's name as a code, and the UNLISTED share link (#1147) will put an access value in a URL. Stripping the query of own URLs closes both with one rule.
- **Cost:** pageviews and autocapture are off (`analytics-service.ts:352-355`), so no current analysis reads query strings. The catalog (`docs/analytics/event-catalog.md`) is unchanged: no event is added or removed.
- **Rejected — stripping only `ref`:** every new sensitive parameter would need another rule.

## Risks / Trade-offs

- [A tampered client sends any code, or a code for another Series] → Counts only; no reward and no access depend on it (D2).
- [A shared device carries one fan's code into another fan's purchase] → Accepted. The code is not personal data, and it expires in 7 days.
- [A code chosen as a person's name, or a future access token in a URL (#1147), reaching an outside analytics service] → D11 strips the query from the app's own URLs before any event leaves the device.
- [Record adds one write and one row lock to every Start that carries a code] → One indexed row per source. Starts without a code skip it.
- [Renaming the IndexedDB databases drops the WalletPublicKey private key and the Scanner keys on existing devices] → Verified recovery paths in D9; task 6.4 handles Scanners before an event.
- [Copy-pasted `?ref=` URLs with typos create stray groups] → Visible in the table; the Organizer hands out links, not typed codes.

## Migration Plan

1. specification: the plan PR (tasks 1.x), then the proto PR and Release → BSR gen.
2. backend PR: migration (`referrals`), entity, repository, usecases, handlers. Deploy to prod; the AtlasMigration status shows the migration applied. Old frontends keep working: the new request field is optional and the new response field is ignored.
3. frontend PR: fan capture and send, organizer Sales tab, Privacy Policy, storage-name clean-up. Before the deploy, run the Scanner check of task 6.4.
4. Verify in production (group 8).
5. Rollback: the migration only adds a table. Rolling back the backend image leaves `referrals` unused; drop it with a forward migration only if the feature is abandoned. A frontend rollback restores the old storage names, and devices lose those values once more.

## Assumptions to confirm

- **A1 — Confirmed 2026-10-15: codes are lowercased** (see D2). Typing `Member-A` and `member-a` must not split one promoter's count.
- **A2 — A failed Record fails Start** (D3). The alternative is to log it and continue the purchase without attribution.
- **A3 — Confirmed 2026-10-15: the Privacy Policy also gains the missing purchase-records category** (D10), not only the purchase route. Adding only the route would list where purchases come from without the purchases themselves.
- **A4 — The Sales tab section appears when the event has at least one sale.** With a sale and no Paid Order it says まだ購入はありません.
- **A5 — The kept code is not cleared by a purchase.** Further purchases of the same Series within 7 days count for the same link.
- **A6 — When the fan changes the ticket count, the new Checkout or Draft is attributed from the code sent with that Start.** The Referral of the released one stays and is never counted.
- **A7 — No cleanup of old storage entries, IndexedDB databases or caches.** They stay unused on the owner's and the tester's devices; clearing site data removes them.
