## ADDED Requirements

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

### Requirement: Webhook Authentication via Zitadel-Issued JWT

The webhook endpoint SHALL authenticate incoming requests by validating the `PAYLOAD_TYPE_JWT` body as a JWT signed by the configured Zitadel instance, using the same JWKS endpoint that the existing backend JWT validator trusts.

**Rationale**: Reusing the JWKS trust chain avoids introducing an additional shared HMAC secret, cuts one secret from the deployment, and provides asymmetric-key authentication where the backend never holds a signing secret.

#### Scenario: Request with valid Zitadel-issued JWT is accepted

- **WHEN** the webhook receives a request whose JWT body is signed by the Zitadel instance and has not expired
- **THEN** the endpoint SHALL proceed to produce the claim-injection response

#### Scenario: Request with invalid JWT is rejected

- **WHEN** the webhook receives a request whose JWT signature fails verification, has expired, or was signed by an unknown issuer
- **THEN** the endpoint SHALL return HTTP 401
- **AND** the endpoint SHALL log the authentication failure with correlation metadata for security monitoring

#### Scenario: Request without a JWT body is rejected

- **WHEN** the webhook receives a request with an empty body or a non-JWT body
- **THEN** the endpoint SHALL return HTTP 400
- **AND** the endpoint SHALL log the malformed-request event

### Requirement: Webhook Reachable Only Within Cluster

The webhook endpoint SHALL be reachable from the in-cluster Zitadel Target endpoint DNS name and SHALL NOT be exposed externally through the GKE Gateway.

**Rationale**: Webhook traffic is internal service-to-service communication; exposing it to the public internet broadens the attack surface for no functional benefit.

#### Scenario: In-cluster call from Zitadel succeeds

- **WHEN** the Zitadel pod invokes the Target endpoint using the in-cluster Service DNS name
- **THEN** the call SHALL reach the backend handler

#### Scenario: External call from the internet is blocked

- **WHEN** a request arrives at the backend's public Gateway hostname for path `/pre-access-token`
- **THEN** the Gateway SHALL NOT route it to the webhook handler
- **AND** the request SHALL receive a 404 or equivalent routing rejection
