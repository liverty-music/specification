## Context

After onboarding and sign-up, the frontend console shows a red 404 error from `UserService/Get` for new users, a redundant second Get RPC after provisioning, a `TypeError: this.client.listByUser is not a function` from an outdated BSR dependency, flooding `isMatch()` debug logs from Aurelia Router, and visual issues on the My Artists hype slider (tap highlight flash, visible grid lines).

The current `UserService/Get` returns `NOT_FOUND` for unregistered users. While semantically correct, this produces an unavoidable browser console error because `fetch()` logs all non-2xx responses. The `CreateResponse` already includes a `user` field, but the frontend discards it and makes an extra Get call.

## Goals / Non-Goals

**Goals:**
- Remove the redundant UserService/Get RPC after provisioning
- Fix TicketJourneyService runtime error by updating BSR dependency
- Reduce console noise from Aurelia Router debug logs in production
- Remove mobile tap highlight and track grid lines from hype slider

**Non-Goals:**
- Changing hype dot glow/animation styling
- Refactoring the overall auth callback flow
- Adding new RPC methods or proto fields

## Decisions

### D1: Keep UserService/Get NOT_FOUND behavior

**Decision**: `UserService/Get` continues to return `NOT_FOUND` when no user record exists. The 404 console error on new user sign-up is accepted as a cosmetic issue.

**Rationale**: Changing the error contract is a breaking change across the proto/backend/frontend boundary. The 404 is only visible in the developer console and does not affect user experience. The frontend already handles it correctly via `ConnectError.NotFound` catch.

### D2: Frontend create() returns User and caches it

**Decision**: `UserRpcClient.create()` returns `User` from `CreateResponse.user`. `UserServiceClient.create()` sets `_current` from the returned value. The second `ensureLoaded()` call in `auth-callback-route.ts` is removed.

**Rationale**: `CreateResponse` already includes the full `User` entity. The backend populates it through the entire chain (repository → usecase → handler → mapper). Discarding it and re-fetching is a wasted RPC call adding ~37ms latency to sign-up.

### D3: Environment-aware LogLevel

**Decision**: Set `LogLevel.debug` only when `import.meta.env.DEV` is true; use `LogLevel.warn` otherwise.

**Rationale**: Aurelia Router emits many `DBG` level logs (e.g., `isMatch()` for every route candidate on each navigation). These are useful during development but flood the console and OTel sink in production. Vite's dead-code elimination ensures the debug sink code is tree-shaken in production builds.

### D4: Tap highlight reset in @layer reset

**Decision**: Add `-webkit-tap-highlight-color: transparent` to the universal reset selector in `reset.css` (`@layer reset`), not in the block-level component CSS.

**Rationale**: CUBE CSS methodology — browser default resets belong in the reset layer. This applies globally to all interactive elements, which is correct since the app provides its own visual feedback for all tap targets.

### D5: Remove hype track grid line

**Decision**: Delete the `.hype-col:first-of-type > &::before` pseudo-element that draws the horizontal track line across hype columns.

**Rationale**: The line is barely visible and adds visual noise. The hype dots themselves provide sufficient visual affordance for the slider interaction.

## Risks / Trade-offs

- **[D1 Console 404]** → Accepted: the 404 on `UserService/Get` for new users is a developer-only cosmetic issue. No user-facing impact.
- **[D3 Log suppression]** → Trade-off: production logs below `warn` level will not appear in console or OTel. This is acceptable since `INF`/`DBG` level logs are for development. If production debugging is needed, the OTel collector can be configured independently.
- **[D5 Track line removal]** → Low risk: purely cosmetic change with no functional impact.
