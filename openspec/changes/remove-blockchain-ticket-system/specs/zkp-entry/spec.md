## REMOVED Requirements

### Requirement: GetMerklePath request carries explicit user_id
**Reason**: The `EntryService` ZKP entry flow is removed under the Scenario A pivot. In a single-operator (verifier == issuer == DB owner) architecture the ZKP privacy guarantee is vacuous, and a signed rotating-QR scheme meets the entry requirement with instant generation and full offline verification.
**Migration**: No live consumer. Web2 entry verification will be defined by the follow-up Web2 ticket change.

### Requirement: VerifyEntry remains unauthenticated
**Reason**: Part of the removed `EntryService` ZKP entry flow.
**Migration**: Web2 entry verification (signed QR + nullifier as a DB uniqueness guard) will be defined by the follow-up Web2 ticket change.
