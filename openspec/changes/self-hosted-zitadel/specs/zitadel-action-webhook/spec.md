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

The webhook endpoint SHALL authenticate incoming requests by validating the `PAYLOAD_TYPE_JWT` body as a JWT signed by the configured Zitadel instance, using the same JWKS endpoint that the existing backend JWT validator trusts, AND SHALL pin a per-endpoint `aud` (audience) claim distinct from the end-user access-token audience so that a captured end-user access token cannot be replayed against the webhook endpoint.

**Rationale**: Reusing the JWKS trust chain avoids introducing an additional shared HMAC secret, cuts one secret from the deployment, and provides asymmetric-key authentication where the backend never holds a signing secret. Because end-user access tokens and webhook JWTs are signed by the same JWKS, signature + issuer + expiry checks alone cannot distinguish them — the per-endpoint `aud` check (e.g., `urn:liverty-music:webhook:pre-access-token`) is the load-bearing defense against access-token replay against the webhook surface. This Requirement intentionally mirrors `authentication/spec.md` "Validate Zitadel Actions v2 Webhook JWTs"; the two specs describe the same defense from different angles (this one from the webhook endpoint's contract, the authentication spec from the JWT validator's contract).

#### Scenario: Request with valid Zitadel-issued JWT is accepted

- **WHEN** the webhook receives a request whose JWT body is signed by the Zitadel instance, has not expired, and whose `aud` claim matches the endpoint's configured webhook audience
- **THEN** the endpoint SHALL proceed to produce the claim-injection response

#### Scenario: Request with invalid JWT is rejected

- **WHEN** the webhook receives a request whose JWT signature fails verification, has expired, was signed by an unknown issuer, or carries an `aud` claim that does not match the endpoint's configured webhook audience
- **THEN** the endpoint SHALL return HTTP 401
- **AND** the endpoint SHALL log the authentication failure with correlation metadata for security monitoring

#### Scenario: End-user access token replay against webhook is rejected

- **WHEN** the webhook receives a request whose JWT body is a valid end-user access token (correct signature, issuer, expiry against the same JWKS) but whose `aud` claim is the end-user access-token audience rather than the webhook-specific audience
- **THEN** the endpoint SHALL return HTTP 401
- **AND** the endpoint SHALL NOT act on the webhook payload

#### Scenario: Request without a JWT body is rejected

- **WHEN** the webhook receives a request with an empty body or a non-JWT body
- **THEN** the endpoint SHALL return HTTP 400
- **AND** the endpoint SHALL log the malformed-request event

### Requirement: Webhook Reachable Only Within Cluster

The webhook endpoints SHALL be served on a dedicated backend port (`:9090`) behind a dedicated in-cluster `Service` (`server-webhook-svc`), distinct from the public Connect-RPC port (`:8080` / `server-svc`). The existing GKE Gateway / `HTTPRoute` SHALL continue to reference only `server-svc`. The webhook **handler** SHALL therefore be unreachable from the public hostname because no handler is registered on the `:8080` listener for webhook paths; the public `:8080` listener's `authn.Middleware` provides defense-in-depth by rejecting any unauthenticated request before the request mux dispatches.

**Rationale**: Webhook traffic is internal service-to-service communication; exposing it to the public internet broadens the attack surface for no functional benefit. The primary defense is **physical listener separation** — the webhook handler binds only to `:9090`, which is fronted exclusively by the in-cluster `server-webhook-svc` and never by the public Gateway. The Gateway's `server-route` HTTPRoute uses a `/*` catch-all and so DOES route a public request for `/pre-access-token` to the backend Pod's `:8080` listener; the secondary defense (rejection at `authn.Middleware`) handles that case. The two layers eliminate any dependency on negative-match routing rules or per-path filters.

#### Scenario: In-cluster call from Zitadel succeeds

- **WHEN** the Zitadel pod POSTs to `http://server-webhook-svc.backend.svc.cluster.local:9090/pre-access-token` (or `/auto-verify-email`)
- **THEN** the call SHALL reach the backend webhook handler on port `9090`

#### Scenario: External call from the internet is blocked

- **WHEN** a request arrives at the backend's public Gateway hostname for path `/pre-access-token` or `/auto-verify-email`
- **THEN** the request SHALL NOT reach any webhook handler
- **AND** the request SHALL receive a 401 from `authn.Middleware` (the existing `server-route` `/*` catch-all forwards the request to `server-svc:80`, where `authn.Middleware` rejects unauthenticated requests before the mux dispatches; the public `:8080` listener has no handler registered for webhook paths)

> **Note**: A future follow-up MAY tighten the `server-route` HTTPRoute to enumerate only public paths, at which point the rejection upgrades to a Gateway-level 404 without changing the security outcome (external requests cannot reach the webhook handler in either case).

#### Scenario: Public Connect-RPC listener does not serve webhooks

- **WHEN** an in-cluster client POSTs to `http://server-svc.backend.svc.cluster.local/pre-access-token` on port `80`
- **THEN** the public Connect-RPC listener on port `8080` SHALL NOT expose webhook routes
- **AND** the request SHALL receive a 404
