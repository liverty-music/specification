## Why

During onboarding, unauthenticated (guest) users can open the concert detail sheet and see Ticket Status buttons (TRACKING / APPLIED / LOST / UNPAID / PAID). Clicking any button triggers a `SetStatus` RPC call, which fails with a 401 Unauthorized error because no bearer token is present. The feature is not meaningful without an account, so it should not be shown to guests at all.

## What Changes

- Hide the Ticket Status section in `EventDetailSheet` when the user is not authenticated
- Remove the error-prone RPC call path for unauthenticated users (no auth guard existed)

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `ticket-journey`: Add frontend visibility requirement — the Ticket Status UI SHALL only be rendered when the user is authenticated. Unauthenticated users SHALL NOT see the section.

## Impact

- **Frontend**: `EventDetailSheet` component (`event-detail-sheet.ts` / `.html`) — conditional rendering of the Ticket Status section based on `authService.isAuthenticated`
- **No backend changes**: The RPC itself remains authenticated-only; this change prevents the UI from attempting unauthenticated calls
- **No proto changes**: No API contract changes
