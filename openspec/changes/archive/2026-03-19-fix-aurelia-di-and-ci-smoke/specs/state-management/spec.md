## ADDED Requirements

### Requirement: Store resolution requires active DI context
The `resolveStore()` helper and any direct `resolve(IStore)` call SHALL only be used within an active Aurelia DI context (class field initializers of DI-managed classes, constructors, or lifecycle hooks). The `IStore` registration via `StateDefaultConfiguration.init()` SHALL be compatible with Aurelia's `resolve()` function at class field initialization time.

#### Scenario: Service resolves IStore at field initialization
- **WHEN** a DI-managed service class uses `resolveStore()` at field initialization time (e.g., `private readonly store = resolveStore()`)
- **THEN** the DI container SHALL successfully resolve `IStore` and return the singleton store instance
- **AND** no AUR0016 error SHALL be thrown

#### Scenario: Route component resolves IStore at field initialization
- **WHEN** a route component uses `resolveStore()` at field initialization time
- **THEN** the DI container SHALL successfully resolve `IStore` and return the singleton store instance
- **AND** no AUR0016 error SHALL be thrown

#### Scenario: Application boots without DI resolution errors
- **WHEN** the Aurelia application starts with `StateDefaultConfiguration.init()` registered
- **THEN** all pages SHALL render without AUR0016 or similar DI resolution errors
- **AND** the E2E smoke test SHALL detect zero console errors on public routes
