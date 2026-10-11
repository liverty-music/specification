# Spec Delta

## REMOVED Requirements

### Requirement: Stalled checkouts finished within one minute
**Reason**: IssueDueReservations is renamed IssueDueCheckouts and finishes stalled Checkouts.
**Migration**: The behavior continues in `components/usecase/order/issue-due-checkouts`; the data moves in this change's migration.

### Requirement: A charged checkout left unissued is reported
**Reason**: IssueDueReservations is renamed IssueDueCheckouts and finishes stalled Checkouts.
**Migration**: The behavior continues in `components/usecase/order/issue-due-checkouts`; the data moves in this change's migration.
