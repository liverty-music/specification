## Context

Currently, Liverty Music requires Passkey authentication via Zitadel before a user can access any protected route (Artist Discovery, Dashboard, My Artists). The `frontend-route-guard` enforces default-deny on all routes except LP, About, and the OIDC callback. This means users must commit to account creation before experiencing any product value.

The linear tutorial approach replaces this with a step-locked guest flow that defers authentication to the final step. The frontend manages two pieces of local state: `onboardingStep` (numeric progression) and `isAuthenticated` (token validity). Read-only RPCs (`ListTop`, `ListSimilar`, `Search`, `ConcertService/List`) are made publicly accessible on the backend so that onboarding users can experience the core product without authentication. Write RPCs (`Follow`, `Unfollow`, `SetPassionLevel`) are handled by a local client that persists to LocalStorage during onboarding and merges to the backend on sign-up completion.

## Goals / Non-Goals

**Goals:**
- Defer sign-up to after product value is demonstrated (Artist Discovery → Dashboard → Passion Level)
- Maintain a simple, linear state machine with no branching guest/auth paths per screen
- Support tutorial interruption and resumption across browser sessions
- Support multi-device scenarios where an authenticated user on a new device skips the tutorial
- Reuse existing backend RPCs for guest data merge (no new API endpoints)
- Allow onboarding users to experience real data from public read-only RPCs (not mock data)

**Non-Goals:**
- Server-side guest session storage (all guest state is client-side LocalStorage)
- A/B testing infrastructure for tutorial variants
- Google OAuth or any non-Passkey authentication method

## Decisions

### Decision 1: `onboardingStep` as numeric enum in LocalStorage

Store tutorial progression as a numeric value (0-6, 7=COMPLETED) in LocalStorage under a well-known key (e.g., `liverty:onboardingStep`).

**Rationale**: A single numeric value is trivial to persist, compare, and restore. It avoids complex state objects and makes the routing guard logic a simple numeric comparison.

**Alternatives considered**:
- Boolean `isOnboarding`: Cannot resume from a specific step after interruption.
- `@aurelia/state` plugin with persistence middleware: The plugin has no built-in persistence; a custom middleware would add abstraction over what is ultimately a single LocalStorage key.
- SessionStorage: Does not survive tab close, preventing cross-session resumption.

### Decision 2: Guest data stored as structured LocalStorage entries

During the tutorial, guest actions (followed artists, passion levels, selected region) are stored as JSON in LocalStorage under namespaced keys (e.g., `liverty:guest:followedArtists`, `liverty:guest:region`).

**Rationale**: Keeps guest data independent from the app's runtime state. On authentication, the merge logic reads these keys, calls backend RPCs, and clears them. If the user clears browser data, they simply restart the tutorial — no orphaned server-side state.

**Alternatives considered**:
- In-memory only (Aurelia service singleton): Lost on page reload, forcing tutorial restart.
- IndexedDB: Over-engineered for a small amount of structured data.

### Decision 3: Route guard evaluates `isAuthenticated` before `onboardingStep`

The routing decision follows a strict priority:

```
1. isAuthenticated === true  → Dashboard (unrestricted), skip everything
2. onboardingStep === COMPLETED → LP with [Login] only
3. onboardingStep in [1..6] → Resume at Step N
4. default → LP with [Get Started] + [Login]
```

**Rationale**: `isAuthenticated` as the highest priority ensures that a user who logs in on a new device (where `onboardingStep` is unset or 0) is never forced into the tutorial. This is critical for multi-device UX.

**Alternatives considered**:
- Check `onboardingStep` first: Would force returning users through the tutorial on new devices.

### Decision 4: Coach mark overlay as a shared component

A single `<coach-mark>` custom element handles the spotlight effect (dimmed overlay with a highlighted target element), tooltip text, and interaction lock. Each tutorial step configures it with a CSS selector for the target element and the instructional message.

**Rationale**: A shared component avoids duplicating overlay logic across Dashboard, Detail BottomSheet, and My Artists screens. The coach mark is controlled by `onboardingStep` — it renders only when the current step matches.

### Decision 5: SignUp modal is non-dismissible at Step 6

The Passkey authentication modal at Step 6 has no close button and no backdrop dismiss. On page reload with `onboardingStep === 6`, the modal re-appears immediately.

**Rationale**: At this point the user has invested effort (selected artists, explored dashboard, set passion level). Making the modal non-dismissible converts this sunk cost into sign-up completion. The user can still abandon by closing the browser tab, but the tutorial will resume at Step 6 on return.

### Decision 6: Data merge sequence after Passkey authentication

After successful Passkey auth at Step 6:
1. `UserService.Create` — provisions the local user record (idempotent via `ALREADY_EXISTS` handling)
2. `ArtistService.Follow` × N — one call per locally followed artist
3. `ArtistService.SetPassionLevel` — for each artist with a non-default passion level
4. Set `onboardingStep = COMPLETED` in LocalStorage
5. Clear guest data keys from LocalStorage
6. Remove all tutorial UI restrictions

**Rationale**: Sequential calls ensure the user record exists before artist operations. The existing RPCs handle all cases without modification.

### Decision 7: Read-only RPCs are public, write RPCs use a local client during onboarding

The onboarding flow requires real backend data (artist charts, concert schedules) to demonstrate product value. Rather than using mock data, read-only RPCs are made publicly accessible on the backend, and write operations are intercepted at the service client layer.

**Public RPCs** (backend `authn-go` allowlist — no token required):
- `ArtistService/ListTop` — artist charts for discovery bubbles
- `ArtistService/ListSimilar` — similar artist expansion on bubble tap
- `ArtistService/Search` — artist search
- `ConcertService/List` — concert schedule per artist

**Authenticated RPCs** (unchanged):
- `ArtistService/Follow`, `Unfollow`, `SetPassionLevel`, `ListFollowed`
- `ConcertService/ListByFollower`, `SearchNewConcerts`
- `UserService/Create`

**Backend implementation**: The `authn.AuthFunc` in `internal/infrastructure/auth/authn.go` checks `req.URL.Path` against a set of public procedures. For public procedures: if no token is present, return `nil, nil` (pass-through with no claims); if a token is present, validate it normally so authenticated users still get claims on context.

**Frontend service client layer**: `ArtistServiceClient` and `ConcertServiceClient` check `OnboardingService.isOnboarding` before each write RPC. During onboarding, write operations persist to LocalStorage via a local client; read operations hit the backend directly (public RPCs). This makes the onboarding/authenticated split transparent to page components — they call the same service methods regardless of mode.

**Rationale**: Using real data during onboarding gives users an authentic preview of the product. The service client abstraction avoids scattering `if (isOnboarding)` checks across page components. The backend allowlist is minimal (4 read-only endpoints) and follows the principle of least privilege.

### Decision 8: `SetPassionLevel` and `Unfollow` are disabled during onboarding UI

During onboarding, `SetPassionLevel` is not invokable — the coach mark at Step 5 demonstrates the concept of passion-level-based push notification control without actually executing the RPC or persisting a level change. The UI shows the passion level toggle visually but does not call any service method.

`Unfollow` is similarly blocked during onboarding. The My Artists page does not offer swipe-to-unfollow or long-press-to-unfollow interactions while `isOnboarding` is true.

**Rationale**: The purpose of Steps 3-5 is to demonstrate features, not to let users modify state that would need complex merge logic. Passion level explanation and notification control messaging can be shown without actual state changes.

### Decision 9: Dashboard uses `ConcertService/List` per artist during onboarding

During onboarding, the Dashboard cannot call `ConcertService/ListByFollower` (requires authentication — it identifies the user by their token). Instead, the `ConcertServiceClient` reads the locally followed artist IDs from LocalStorage and calls `ConcertService/List` (public) for each artist, merging the results.

Similarly, `ArtistService/ListFollowed` is replaced by reading followed artist data from LocalStorage during onboarding.

**Rationale**: `ListByFollower` is inherently user-scoped (it uses the JWT subject to identify which artists to query). Making it public would require passing artist IDs as request parameters, which changes the API contract. Using per-artist `List` calls with locally stored IDs achieves the same result without API changes.

### Decision 10: Naming conventions — `isOnboarding` and `localClient`

- All onboarding state checks use `isOnboarding` (not `isInTutorial`, `isGuest`, etc.) for consistency with the `onboardingStep` state machine.
- The LocalStorage-backed client is named `localClient` with method names matching the RPC interface (`follow`, `unfollow`, `listFollowed`, etc.). This avoids "guest data" or "mock" naming that misrepresents the purpose — it is a local persistence layer with the same interface as the remote client.

## Risks / Trade-offs

- **[LocalStorage cleared by user]** → Tutorial restarts from Step 0. Guest data is lost. Acceptable for MVP; no server-side recovery needed.
- **[User completes tutorial on Device A, accesses on Device B]** → Device B has no `onboardingStep`. Mitigated by Decision 3: `isAuthenticated = true` bypasses tutorial entirely.
- **[Slow network during data merge]** → Multiple sequential RPC calls at Step 6 could feel slow. Mitigation: Show a loading spinner during merge. Consider batching Follow calls in a future iteration.
- **[Coach mark target element not rendered]** → If the highlighted element is not in the DOM (e.g., no concert data), the tutorial could stall. Mitigation: Ensure Step 3 (Dashboard) always has at least one concert card by using seed data or a fallback state.
- **[onboardingStep = 6 but Zitadel is down]** → User is stuck on non-dismissible modal. Mitigation: Show an error state with retry button within the modal. Do not allow dismissal.
- **[Public RPCs abused]** → `ListTop`, `ListSimilar`, `Search`, `ConcertService/List` are now publicly accessible without authentication. Mitigation: These are read-only endpoints returning publicly available data (artist charts, concert schedules). Rate limiting at the infrastructure level (Cloud Armor / API Gateway) mitigates abuse. No user-specific data is exposed.
- **[Multiple ConcertService/List calls during onboarding Dashboard]** → One RPC per followed artist (up to 3 in the tutorial) instead of a single `ListByFollower`. Acceptable for the tutorial's small dataset. Not a scalability concern.
