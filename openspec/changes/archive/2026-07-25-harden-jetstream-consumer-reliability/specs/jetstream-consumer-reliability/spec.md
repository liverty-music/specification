## ADDED Requirements

### Requirement: Durable configuration is reconciled on startup

The consumer SHALL reconcile each durable it owns against the desired configuration at startup. When a durable's server-stored configuration (name, deliver group, or delivery policy) has drifted from the desired configuration, the consumer SHALL recreate the durable so that a configuration or naming change cannot wedge on a stale pre-existing durable.

#### Scenario: A pre-existing durable has drifted configuration

- **WHEN** a durable exists on the server with a configuration that differs from the consumer's desired configuration
- **THEN** the consumer SHALL delete and recreate that durable to match the desired configuration before consuming

#### Scenario: An already-correct durable is left untouched

- **WHEN** a durable already matches the desired configuration
- **THEN** the consumer SHALL bind to it without deleting or recreating it
