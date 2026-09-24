<!-- merge_group: WEBHOOK-PRE-ACCESS-TOKEN | target: components/adapter/fan/api/webhook/pre-access-token | members: 2 -->

<!-- member: zitadel-action-webhook | flags: CLASSNAME -->
### Requirement: Pre-Access-Token Webhook Endpoint

The backend SHALL expose an HTTP endpoint at `POST /pre-access-token` that Zitadel invokes as an Actions v2 Target to inject custom claims into outgoing access tokens before they are signed.

**Rationale**: Zitadel v4 replaces the in-process Actions v1 JavaScript mechanism with external webhook Targets. The email-claim injection previously implemented as inline JS must migrate to a backend-hosted HTTP handler.

#### Scenario: Valid webhook request receives claim injection response

- **WHEN** Zitadel POSTs a `preaccesstoken` payload to `/pre-access-token` with a valid `PAYLOAD_TYPE_JWT` body
- **THEN** the endpoint SHALL return HTTP 200
- **AND** the response body SHALL be a JSON object with an `append_claims` array
- **AND** the `append_claims` array SHALL contain `{"key":"email","value":<user.human.email>}` when the user has a verified email address
- **AND** the response content type SHALL be `application/json`

#### Scenario: Machine user request is passed through without email

- **WHEN** the webhook payload describes a machine user (no `user.human.email`)
- **THEN** the endpoint SHALL return HTTP 200
- **AND** the response SHALL omit the `email` entry from `append_claims`

<!-- member: zitadel-action-webhook | flags:  -->
### Requirement: Webhook Authentication via Zitadel-Issued JWT Signature

The webhook endpoint SHALL authenticate incoming requests by validating the `PAYLOAD_TYPE_JWT` body as a JWT signed by the configured Zitadel instance, using the same JWKS endpoint that the existing backend JWT validator trusts. Signature verification is the sole authenticity check; the validator SHALL NOT enforce `iss` or `aud` claims because Zitadel v4 webhook JWTs do not populate them.

**Rationale**: Empirically Zitadel v4 webhook JWTs (`PAYLOAD_TYPE_JWT`) carry only application-specific private claims plus standard `exp` / `iat` for replay protection — `iss` comes through as empty string, `aud` as empty array. The original spec assumed Zitadel populated these the way OIDC access tokens do, and pinned a per-endpoint `aud` value (`urn:liverty-music:webhook:pre-access-token`) as the security boundary against access-token replay against the webhook surface. That boundary collapsed when the empirical contract turned out to differ — the validator rejected every webhook call with `webhook token issuer "" is not in the accepted issuers list` and then with `webhook token audience [] does not contain expected ...` until both checks were dropped (backend#288, backend#289).

The replacement security boundary is a defense-in-depth stack:

1. **JWT signature (JWKS)** — proves origin: only Zitadel holds the corresponding private key. External attackers cannot forge a valid signature regardless of claim contents.
2. **Network isolation** — the webhook listener is `:9090` ClusterIP-only, not exposed externally. Untrusted clients cannot reach it.
3. **Per-handler payload-shape checks** — each handler decodes handler-specific private claims (e.g. `user.human.email` for `pre-access-token`); a JWT minted for a different webhook would fail the handler's payload-shape expectations even if signature passes.

The upstream community Go reference implementation ([xianyu-one/zitadel-mapping](https://github.com/xianyu-one/zitadel-mapping/blob/main/main.go)) follows the same pattern (signature-only, no `iss` / `aud` enforcement), confirming this is the documented contract for self-hosted Zitadel v4 webhook recipients.

#### Scenario: Request with valid JWT signature is accepted

- **WHEN** the webhook receives a request whose JWT body is signed by the Zitadel instance and has not expired
- **THEN** the endpoint SHALL proceed to produce the claim-injection response
- **AND** the endpoint SHALL NOT reject the request based on `iss` or `aud` claim contents

#### Scenario: Request with invalid signature is rejected

- **WHEN** the webhook receives a request whose JWT signature fails verification, has expired, or is malformed
- **THEN** the endpoint SHALL return HTTP 401
- **AND** the endpoint SHALL log the authentication failure with correlation metadata for security monitoring

#### Scenario: Request without a JWT body is rejected

- **WHEN** the webhook receives a request with an empty body or a non-JWT body
- **THEN** the endpoint SHALL return HTTP 400
- **AND** the endpoint SHALL log the malformed-request event

