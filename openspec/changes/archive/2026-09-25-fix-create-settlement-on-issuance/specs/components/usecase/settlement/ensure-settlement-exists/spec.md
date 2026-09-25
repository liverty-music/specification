# Spec Delta

## REMOVED Requirements

### Requirement: Every issued order gets a Held settlement

**Reason**: Superseded by `Order.Issue`, which now stores the Held Settlement atomically with the Order and its Tickets at issuance time (backend#468). Nothing in production ever called `EnsureSettlementExists` — it was dead code.
**Migration**: None. No Settlement was ever created by this path, so there is no data to migrate; new issuances are settled via `Order.Issue`.
