## ADDED Requirements

### Requirement: Identity service health reflects only the process

The identity service has no database. Its liveness check SHALL report alive whenever the process can answer it. Its readiness check SHALL report ready once it accepts requests from its callers, and not ready while it is shutting down. Neither check SHALL depend on whether the identity provider is reachable; while the identity provider is unreachable, a request to the identity service SHALL fail with Unavailable.

#### Scenario: Identity provider unreachable

- **WHEN** the identity provider cannot be reached
- **THEN** the identity service stays alive and ready, and a request to it fails with Unavailable

#### Scenario: Identity service shutting down

- **WHEN** the identity service is shutting down
- **THEN** its readiness check reports not ready
