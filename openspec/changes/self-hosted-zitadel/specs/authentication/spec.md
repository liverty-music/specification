## ADDED Requirements

### Requirement: Validate Zitadel Actions v2 Webhook JWTs

The backend SHALL validate the authenticity of incoming Zitadel Actions v2 webhook requests by verifying the JWT payload body against the same JWKS endpoint that the backend already trusts for end-user access-token validation, and SHALL reject any request whose JWT signature, issuer, expiry, or audience fails verification.

**Rationale**: The Actions v2 webhook authentication model uses Zitadel-signed JWTs (`PAYLOAD_TYPE_JWT`) in place of a shared HMAC secret. Reusing the existing JWKS trust chain gives asymmetric-key verification without adding a rotatable shared secret or a second trust anchor. Because end-user access tokens are signed by the same JWKS, the `aud` (audience) claim MUST be pinned to a webhook-specific value so that a captured end-user access token cannot be replayed against the webhook endpoint.

#### Scenario: Webhook request with valid JWT passes verification

- **WHEN** the backend receives a webhook request whose body is a JWT signed by the configured Zitadel instance
- **THEN** the backend SHALL verify the JWT signature using the Zitadel JWKS
- **AND** the backend SHALL verify the token has not expired
- **AND** the backend SHALL verify the issuer claim matches the configured Zitadel issuer URL
- **AND** the backend SHALL verify the `aud` claim matches the configured webhook audience for the target endpoint (distinct from the end-user access-token audience)
- **AND** the backend SHALL proceed to process the webhook payload

#### Scenario: Webhook request with invalid JWT is rejected

- **WHEN** the backend receives a webhook request whose JWT signature is invalid, has expired, was signed by an unknown issuer, or carries an audience that does not match the endpoint's configured webhook audience
- **THEN** the backend SHALL reject the request with HTTP 401
- **AND** the backend SHALL NOT act on the webhook payload

#### Scenario: End-user access token replay against webhook is rejected

- **WHEN** the backend receives a webhook request whose JWT is a valid end-user access token (correct signature, issuer, expiry) but carries the end-user access-token audience rather than the webhook-specific audience
- **THEN** the backend SHALL reject the request with HTTP 401
- **AND** the backend SHALL NOT act on the webhook payload

#### Scenario: Webhook JWT validator shares the existing JWKS cache

- **WHEN** the backend services a webhook request
- **THEN** the validator SHALL use the same JWKS cache and refresh cadence (default `15m`) already established for end-user access-token validation
- **AND** the validator SHALL NOT open a separate HTTP client or cache for webhook verification
