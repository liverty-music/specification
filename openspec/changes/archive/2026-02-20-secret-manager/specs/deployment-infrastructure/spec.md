## MODIFIED Requirements

### Requirement: Dedicated CD Namespace

The cluster SHALL support dedicated namespaces for Continuous Delivery tooling and cluster-level operators.

#### Scenario: Namespace Existence

- **WHEN** listing namespaces
- **THEN** a namespace named `argocd` (or configured equivalent) is present

#### Scenario: External Secrets namespace

- **WHEN** listing namespaces
- **THEN** a namespace named `external-secrets` is present for the ESO controller
