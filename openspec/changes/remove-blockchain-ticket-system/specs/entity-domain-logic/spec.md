## REMOVED Requirements

### Requirement: ZKP public signal parsing
**Reason**: `ParseZKPPublicSignals` / `ZKPPublicSignals` exist only to support the removed off-chain ZKP `EntryService` verification path.
**Migration**: None; the `entity/zkp_signals.go` code is deleted with the ZKP entry flow.

### Requirement: ZKP event ID verification
**Reason**: `VerifyEventID` operates on the removed `ZKPPublicSignals` type.
**Migration**: None; code deleted.

### Requirement: ZKP byte conversion helpers
**Reason**: These helpers exist solely to translate BN254 field elements for ZKP public-signal handling, which is removed.
**Migration**: None; code deleted.
