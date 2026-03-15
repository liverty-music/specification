## Context

After OIDC authentication, the frontend has access to the identity token (email, preferred_username) via `oidc-client-ts`, but never fetches the backend User entity (which contains business data like `home`). Each page independently decides how to obtain user data:

- **Dashboard**: Calls `UserService.Get` in `loading()` but only checks `resp.user?.home` for a boolean `needsRegion` flag — the full entity is discarded.
- **Settings**: Reads `localStorage('guest.home')` via `UserHomeSelector.getStoredHome()` — never contacts the backend.
- **UserHomeSelector**: On authenticated update, calls `updateHome()` RPC but does not write to localStorage. On next Settings visit, localStorage is stale → "Not set".

The project uses **Service-Based State** (singleton DI services, no external state library) as documented in CLAUDE.md.

## Goals / Non-Goals

**Goals:**
- Provide a single, centralized source of truth for the authenticated user's backend profile in the frontend.
- Ensure the profile is available before any route renders on page load, reload, and after auth callback.
- Fix the "My Home Area: Not set" bug on Settings for authenticated users.
- Maintain the existing guest flow (localStorage-based) unchanged.

**Non-Goals:**
- Introducing an external state management library (e.g., Redux, MobX).
- Adding real-time sync or WebSocket-based profile updates.
- Caching the profile in localStorage or sessionStorage (memory-only is sufficient).
- Modifying the backend `UserService.Get` RPC or protobuf definitions.

## Decisions

### 1. Extend `UserService` with state, not `AuthService`

**Decision**: Add `current: User | undefined` to the existing `UserService` singleton.

**Alternatives considered**:
- **AuthService**: Already holds OIDC `User` (identity token). Adding backend `User` (business entity) mixes authentication concerns with domain data. SRP violation.
- **New `UserProfileService`**: Clean separation but creates redundancy with `UserService` which already owns the RPC client and `updateHome()`.

**Rationale**: `UserService` already owns the RPC client and mutation methods. Adding cached state here maximizes cohesion — the service that fetches and mutates user data also holds the current snapshot.

### 2. Use `AppTask.activating()` for eager load at startup

**Decision**: Register an `AppTask.activating()` hook that awaits `authService.ready` then calls `userService.ensureLoaded()`.

**Alternatives considered**:
- **Lazy load only (`ensureLoaded()` in each page's `loading()`)**: Requires every page to remember to call it. The current bug is literally a "forgot to call" bug — lazy-only recreates the same failure mode.
- **Root component `binding()`**: Works but couples app-shell to user service concerns. AppTask is the Aurelia 2 idiomatic equivalent of Angular's `APP_INITIALIZER`.
- **AuthService constructor triggers load**: Creates circular dependency (`AuthService → UserService → AuthService` via transport).

**Rationale**: AppTask.activating() runs before root component activation and route navigation. It's the Aurelia 2 recommended pattern for async service initialization. Combined with auth-callback load, it covers all entry paths.

### 3. Idempotent `ensureLoaded()` method

**Decision**: `ensureLoaded()` checks `this._current is not undefined` before making an RPC call. Returns immediately if already loaded.

**Rationale**: This method is called from both AppTask (page load/reload) and auth-callback (sign-in/sign-up). Making it idempotent avoids duplicate RPCs when both paths run in the same session.

### 4. Write-through on mutation

**Decision**: `updateHome()` updates `this._current.home` in memory after a successful RPC response.

**Rationale**: The RPC response includes the updated `User` entity. Using the response to update `current` ensures consistency without an extra `get()` call. This is the write-through cache invalidation pattern.

### 5. Clear on sign-out

**Decision**: Add a `clear()` method that sets `_current = undefined`, called during sign-out flow.

**Rationale**: Prevents stale profile data from being visible if a different user signs in on the same browser session.

## Risks / Trade-offs

- **Startup latency**: AppTask adds one `UserService.Get` RPC call (~50ms) before routes render. → Acceptable for data correctness. The call is skipped entirely for unauthenticated/guest users.
- **Stale data during session**: Profile is loaded once and updated only on local mutations. If another device changes the home area, this session won't see it until reload. → Acceptable given the current single-device usage model. No worse than localStorage.
- **Auth-callback race**: If `provisionUser()` calls `create` and the user is brand new, `ensureLoaded()` immediately after should return the just-created user with home. → The `create` RPC is synchronous; by the time `ensureLoaded()` runs, the user exists in the backend.
