## Why

The recent `introduce-coordinates-vo` refactoring moved `Concert.ProximityTo()` into the entity layer, proving that pure business logic belongs with the data it operates on. However, several other pure business rules remain scattered across the usecase layer — validation, classification, deduplication, and construction logic that depend only on entity fields. This makes them harder to test (requiring usecase-level setup with mocks) and harder to reuse. Moving them to the entity layer improves testability, discoverability, and domain cohesion.

## What Changes

- **Move pure business logic to entity layer**: Relocate validation, classification, grouping, and filtering functions from `usecase/` to `entity/` as methods or package-level functions.
- **Add entity constructors with ID generation**: Introduce constructor functions (following the existing `NewArtist` pattern) for entities that currently have inline UUID generation scattered across usecases.
- **Add enum validation methods**: Provide `IsValid()` methods on domain enum types (`Hype`, etc.) to replace ad-hoc `default:` guards.
- **Add comprehensive unit tests**: Cover all newly added entity functions AND existing entity functions that gained testability from prior refactoring (e.g., `Concert.ProximityTo()`).

## Capabilities

### New Capabilities

- `entity-domain-logic`: Covers the entity-layer enrichment — moved business logic, constructors, validation methods, and their comprehensive test coverage.

### Modified Capabilities

(none — no spec-level behavior changes; this is an internal restructuring)

## Impact

- **`internal/entity/`**: New methods, constructors, and package-level functions added. New `_test.go` files created.
- **`internal/usecase/`**: Existing private functions replaced with calls to entity-layer equivalents. Reduced code volume and simplified test setup.
- **No API changes**: No proto, RPC, or database changes. Purely internal refactoring.
- **No migration needed**: No schema or infrastructure impact.
