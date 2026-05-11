## ADDED Requirements

### Requirement: Validate Zitadel Actions v2 Webhook JWTs by Signature

The backend SHALL validate the authenticity of incoming Zitadel Actions v2 webhook requests by verifying the JWT payload body against the same JWKS endpoint that the backend already trusts for end-user access-token validation. The validator SHALL enforce signature + expiry checks only; it SHALL NOT enforce `iss` or `aud` claims because Zitadel v4 webhook JWTs do not populate them.

**Rationale**: The Actions v2 webhook authentication model uses Zitadel-signed JWTs (`PAYLOAD_TYPE_JWT`) in place of a shared HMAC secret. Reusing the existing JWKS trust chain gives asymmetric-key verification without adding a rotatable shared secret or a second trust anchor.

The original spec pinned a per-endpoint `aud` claim (e.g., `urn:liverty-music:webhook:pre-access-token`) as the security boundary against access-token replay, on the assumption that webhook JWTs carried OIDC-shaped claims. **Empirically Zitadel v4 webhook JWTs carry only application-specific private claims plus standard `exp` / `iat`** — `iss` comes through as empty string, `aud` as empty array. Both checks rejected every webhook call until they were dropped (backend#288, backend#289).

The replacement security boundary is a defense-in-depth stack:

1. **JWT signature (JWKS)** — proves origin: only Zitadel holds the corresponding private key.
2. **Network isolation** — the webhook listener is `:9090` ClusterIP-only (see `zitadel-action-webhook` spec).
3. **Per-handler payload-shape checks** — each handler decodes handler-specific private claims; a webhook JWT minted for a different purpose would fail downstream payload validation even if signature passes.

End-user access-token replay against the webhook is mitigated by network isolation (an external attacker cannot reach `:9090`) plus payload-shape mismatch (an end-user access token does not carry `user.human.email` in the same nesting Zitadel uses for webhook payloads).

#### Scenario: Webhook request with valid JWT signature passes verification

- **WHEN** the backend receives a webhook request whose body is a JWT signed by the configured Zitadel instance
- **THEN** the backend SHALL verify the JWT signature using the Zitadel JWKS
- **AND** the backend SHALL verify the token has not expired
- **AND** the backend SHALL proceed to process the webhook payload
- **AND** the backend SHALL NOT reject the request based on `iss` or `aud` claim contents

#### Scenario: Webhook request with invalid signature is rejected

- **WHEN** the backend receives a webhook request whose JWT signature is invalid, has expired, or is malformed
- **THEN** the backend SHALL reject the request with HTTP 401
- **AND** the backend SHALL NOT act on the webhook payload

#### Scenario: Webhook JWT validator shares the existing JWKS cache

- **WHEN** the backend services a webhook request
- **THEN** the validator SHALL use the same JWKS cache and refresh cadence (default `15m`) already established for end-user access-token validation
- **AND** the validator SHALL NOT open a separate HTTP client or cache for webhook verification

> **Forward compatibility**: If a future Zitadel version adds proper `iss` / `aud` claims to webhook JWTs, the validator can re-introduce these checks without breaking the existing contract — the current implementation silently accepts any value (including missing). When that happens, this requirement should be tightened to enforce them.
