## ADDED Requirements

### Requirement: Configure OIDC Token Lifetimes

The system SHALL manage Zitadel instance-level OIDC token lifetimes explicitly via Infrastructure as Code, rather than relying on Zitadel built-in defaults. The configured values SHALL be:

| Setting | Value | Purpose |
|---|---|---|
| `accessTokenLifetime` | `30m` | Short-lived access token limits exposure if leaked; cannot be revoked before expiry once issued. |
| `refreshTokenIdleExpiration` | `30d` | Inactivity window — a refresh token unused for 30 days becomes invalid. |
| `refreshTokenExpiration` | `90d` | Absolute lifetime — after 90 days the user must re-authenticate regardless of activity. |

**Rationale**: A never-miss-a-live notification app benefits from long-lived sessions so fans stay signed in across gaps, while a short access-token lifetime keeps the security exposure window small. Pinning these values in IaC makes the intent durable and reviewable instead of implicitly inheriting whatever Zitadel ships as defaults.

#### Scenario: OIDC token lifetimes provisioned via IaC

- **WHEN** the Zitadel Pulumi stack is applied in an environment
- **THEN** the instance-level OIDC settings SHALL set `accessTokenLifetime` to `30m`
- **AND** SHALL set `refreshTokenIdleExpiration` to `30d`
- **AND** SHALL set `refreshTokenExpiration` to `90d`

#### Scenario: Access token rejected after its lifetime

- **WHEN** an access token is older than `30m`
- **THEN** the backend JWT validation SHALL reject requests bearing that token as expired
- **AND** the client SHALL obtain a fresh access token via the refresh-token grant

#### Scenario: Session ends after refresh token absolute expiry

- **WHEN** a refresh token reaches its `90d` absolute expiration
- **THEN** Zitadel SHALL reject further refresh-token grants for that token
- **AND** the user SHALL be required to re-authenticate
