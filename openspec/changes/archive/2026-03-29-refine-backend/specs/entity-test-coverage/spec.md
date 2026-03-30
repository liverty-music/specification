## ADDED Requirements

### Requirement: SafePredictor interface in entity layer

The entity layer SHALL define a `SafePredictor` interface to decouple the adapter layer from infrastructure blockchain imports.

#### Scenario: TicketHandler uses SafePredictor interface

- **WHEN** TicketHandler needs to compute a Safe address
- **THEN** it SHALL depend on `entity.SafePredictor` interface
- **AND** SHALL NOT import `internal/infrastructure/blockchain/safe` directly

#### Scenario: SafePredictor implementation satisfies interface

- **WHEN** `safe.Predictor` is used as the concrete implementation
- **THEN** it SHALL satisfy the `entity.SafePredictor` interface via compile-time check
