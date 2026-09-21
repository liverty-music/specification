# Pre Access Token

## Purpose

The backend SHALL host the Zitadel Actions v2 webhook endpoints that
inject custom claims into outgoing access tokens before they are
signed. Replaces the prior in-process Actions v1 JavaScript mechanism.
Specifies the endpoint contract, the Zitadel-issued JWT signature
authentication model (signature-only — no `iss`/`aud` enforcement
because Zitadel v4 webhook JWTs do not populate them), and the
in-cluster-only network exposure invariant.

## Requirements

### Requirement: Pre-Access-Token Webhook Endpoint

The backend SHALL expose an HTTP endpoint at `POST /pre-access-token` that Zitadel invokes as an Actions v2 Target to inject custom claims into outgoing access tokens before they are signed. The endpoint SHALL authenticate incoming requests by validating the `PAYLOAD_TYPE_JWT` body as a JWT signed by the configured Zitadel instance, using the same JWKS endpoint that the existing backend JWT validator trusts; signature verification is the sole authenticity check, and the validator SHALL NOT enforce `iss` or `aud` claims because Zitadel v4 webhook JWTs do not populate them.

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
