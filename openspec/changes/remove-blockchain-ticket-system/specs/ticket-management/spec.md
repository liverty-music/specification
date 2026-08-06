## REMOVED Requirements

### Requirement: MintTicket request carries explicit user_id
**Reason**: The on-chain `TicketService` (soulbound minting) is removed under the Scenario A (walled-garden) pivot; blockchain minting provides no load-bearing value for a single-operator platform.
**Migration**: No consumer path is live (frontend ticket nav is hidden; handlers are unreachable without dev-only secrets). A future Web2 ticket capability will define account-bound issuance in a separate change.

### Requirement: ListTickets request carries explicit user_id
**Reason**: Part of the removed on-chain `TicketService`.
**Migration**: Web2 ticket listing will be redefined by the follow-up Web2 ticket change.

### Requirement: GetTicket remains identifier-scoped
**Reason**: Part of the removed on-chain `TicketService`.
**Migration**: Web2 ticket retrieval will be redefined by the follow-up Web2 ticket change.
