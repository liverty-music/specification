## Context

`EventDetailSheet` is rendered both during onboarding (guest) and after authentication. It currently shows the Ticket Status section unconditionally. When a guest user clicks a status button, `setJourneyStatus()` calls `TicketJourneyRpcClient.setStatus()` with no bearer token, resulting in a 401 Unauthorized RPC error.

The existing `AuthService.isAuthenticated` getter is already used throughout the codebase (e.g., `ConcertService`) to guard authenticated-only operations.

## Goals / Non-Goals

**Goals:**
- Prevent the Ticket Status UI from being displayed to unauthenticated users
- Eliminate the 401 error that occurs when guests attempt to set a ticket status

**Non-Goals:**
- Showing a sign-in prompt or CTA in place of the hidden section
- Persisting guest ticket intent for post-signup merge
- Any backend changes

## Decisions

### Decision: Hide the section entirely vs. disable buttons

**Chosen:** Hide the entire Ticket Status section (`if.bind="authService.isAuthenticated"`).

**Alternatives considered:**
- *Disable buttons with a tooltip*: Adds visual complexity for a feature that has no value in guest context. During onboarding, the goal is concert exploration, not ticket management.
- *Replace with sign-in CTA*: Reasonable for a post-onboarding guest, but onboarding is not a sign-up funnel at this stage of the flow. Adds scope.

The simplest approach — hide entirely — matches the intent ("not yet visible") and avoids new UI states.

### Decision: Check `authService.isAuthenticated` in ViewModel vs. template

**Chosen:** Expose `isAuthenticated` as a getter on the ViewModel that delegates to `AuthService`, and use `if.bind` in the template.

This follows the existing Aurelia pattern in the codebase (binding to ViewModel-exposed getters) and keeps the template declarative.

### Decision: Scope of the guard

**Chosen:** Guard applies whenever `isAuthenticated === false`, regardless of whether the user is mid-onboarding or a post-onboarding guest.

The ticket journey feature requires an account in all cases, so the guard condition is simply authentication state.

## Risks / Trade-offs

- **Minimal risk**: Change is purely additive (hiding a section). No existing authenticated flows are affected.
- **No guest fallback needed**: The feature has no meaningful guest analog, so nothing needs to replace it.
