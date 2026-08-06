## REMOVED Requirements

### Requirement: Proof service utility functions perform correct byte-to-field conversions
**Reason**: `proof-service` and its byte-to-field helpers exist only for client-side ZK proof generation, which is removed under the Scenario A pivot.
**Migration**: None; `src/services/proof-service.ts` and its tests are deleted.

### Requirement: Proof service verifies circuit file integrity
**Reason**: No circuit files are served, so integrity verification has no target.
**Migration**: None; code and tests deleted.

### Requirement: Tickets page generates ZK proof entry QR codes
**Reason**: The blockchain tickets route and its ZK proof QR flow are removed.
**Migration**: None; `src/routes/tickets/` and its tests are deleted. A Web2 tickets route will be specified by the follow-up Web2 ticket change.
