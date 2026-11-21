## Context

See proposal.md - Why. The console builds its OIDC configuration once per page load, at bootstrap: the Organization named by the address, else the one remembered in localStorage. The route guard checks after sign-in that the token belongs to that Organization (organizer-shell, "enforce the token's Organization"). The implementation is frontend#1079.

## Decisions

### D1. The address's Organization waits as the tab's pending pin

An Organization named by the address is kept in sessionStorage as the pending pin of the sign-in it starts, not in localStorage. The OIDC callback page of the same tab names the pending pin, else the remembered one, so the guard still enforces the Organization the sign-in was started for. Every other page load drops the pending pin.

Alternative: write the remembered pin at bootstrap and erase it when sign-in fails. Rejected: a sign-in that fails at the hosted login never returns to the console, so nothing could erase it.

Alternative: keep the pending pin in localStorage. Rejected: another tab's page load drops it, and another tab's sign-in replaces it, before this tab's callback reads it.

### D2. The guard remembers the pending pin when it admits the member

The guard remembers the pending pin only when all of these hold: it admits an owner, the owner's token holds a grant in an Organization, and the pending pin is the pin this page load enforces. With nothing pending it writes nothing, so a tab loaded earlier never writes its own pin back over a newer one. A pending pin that differs from the enforced one is dropped. That happens when Back restores a page after a failed sign-in in the same tab.

## Risks / Trade-offs

- [A callback that lands in another tab finds no pending pin] → it names the remembered Organization or none, and the guard's existing check re-authenticates or admits without remembering. Every flow that names an Organization by address starts the sign-in in the tab that opened the address, and the Organizer login policy has no step that continues in a new tab.
