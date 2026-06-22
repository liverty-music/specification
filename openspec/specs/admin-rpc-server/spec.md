## Purpose

A dedicated backend Connect server for admin-scoped RPCs: a separate in-process listener on its own port, serving only admin services, with boundary-level admin-role authorization (replacing per-method checks), an admin-only CORS allowlist, its own ingress host (`api.admin.{env-base-domain}`) / Service / cert / DNS / health, and the consumer server's exclusion of admin services. The admin console's RPC client resolves the admin API host from its runtime config. This isolates the admin surface's governance (origins, limits, host, future IAP) from the public API and makes admin authorization structural rather than per-method discipline.
## Requirements
### Requirement: Dedicated admin Connect server

The backend SHALL serve admin-scoped RPCs from a dedicated Connect server bound to
its own port, separate from the consumer-facing Connect server. Both servers MAY
run in the same backend binary. The admin server SHALL serve ONLY admin-scoped
services, and the consumer server SHALL NOT serve any admin-scoped service.

#### Scenario: Admin service served only on the admin port

- **WHEN** the backend starts
- **THEN** the admin `liverty_music.rpc.admin.v1.ConcertService` is registered on
  the admin server's mux
- **AND** it is NOT registered on the consumer server's mux

#### Scenario: Consumer service served only on the consumer port

- **WHEN** the backend starts
- **THEN** consumer services (e.g. `UserService`, `ArtistService`, and the consumer
  `liverty_music.rpc.concert.v1.ConcertService`) are registered on the consumer
  server
- **AND** they are NOT registered on the admin server

#### Scenario: Both servers drain on shutdown

- **WHEN** the backend receives a shutdown signal
- **THEN** both the consumer and admin servers SHALL drain in-flight requests
  during the shutdown Drain phase

### Requirement: Boundary-level admin authorization

Every RPC served by the admin server SHALL pass through a fixed admin-authorization
layer that requires the caller to hold the `admin` role. Authorization SHALL be
enforced at the server boundary for all admin RPCs uniformly, NOT by per-handler-method
checks. A request that fails this check SHALL be rejected before any handler business
logic executes.

#### Scenario: Admin caller is allowed

- **WHEN** a caller whose validated token carries the `admin` role invokes any admin RPC
- **THEN** the admin-authorization layer SHALL allow the request to reach the handler

#### Scenario: Authenticated non-admin caller is denied

- **WHEN** a caller presents a valid JWT that does NOT carry the `admin` role
- **THEN** the request SHALL be rejected with `PERMISSION_DENIED`
- **AND** no handler business logic SHALL execute

#### Scenario: Unauthenticated caller is denied

- **WHEN** a caller presents no valid token to the admin server
- **THEN** the request SHALL be rejected by the admin server's authn layer (default-deny)

#### Scenario: Admin RPCs carry no per-method role check

- **WHEN** an admin handler method is implemented
- **THEN** it SHALL NOT contain its own per-method role assertion
- **AND** the admin server's boundary layer SHALL be the sole admin-role gate

### Requirement: Admin-only CORS allowlist

The admin server SHALL use a CORS allowlist configured independently of the consumer
server, containing only admin origins. The consumer server's CORS allowlist SHALL NOT
be required to contain the admin origin.

#### Scenario: Admin origin allowed on the admin server

- **WHEN** the admin console origin sends a request to the admin server
- **THEN** the admin server's CORS layer SHALL permit it

#### Scenario: Admin origin not required on the consumer server

- **WHEN** the consumer server's CORS allowlist is configured
- **THEN** it SHALL NOT need to include the admin origin for the admin console to function

### Requirement: Shared server construction to prevent interceptor drift

The consumer and admin Connect servers SHALL be constructed through a shared factory
so that the interceptor chain ordering invariants are identical for both, differing
only by the admin-authorization layer and the CORS allowlist.

#### Scenario: Both servers share the base interceptor chain

- **WHEN** either server is constructed
- **THEN** it SHALL apply the same base interceptor ordering (tracing, rate limiting,
  access log, error handling, panic recovery, claims bridge, validation)
- **AND** the admin server SHALL additionally apply the admin-authorization layer
  (after the claims bridge, before validation)

### Requirement: Dedicated admin API ingress host

The admin server SHALL be reachable at a dedicated hostname `api.admin.{env-base-domain}`
(e.g. `api.admin.dev.liverty-music.app`, `api.admin.liverty-music.app`) via its own
Kubernetes Service and a dedicated HTTPRoute on the shared external gateway, with its
own certificate, DNS entry, and gRPC health check. The consumer API host and routing
SHALL remain unchanged.

#### Scenario: Admin API host routes to the admin server

- **WHEN** a request arrives for `api.admin.{env-base-domain}`
- **THEN** the shared gateway routes it to the admin backend Service

#### Scenario: Consumer API host unchanged

- **WHEN** a request arrives for the consumer API host
- **THEN** it continues to route to the consumer backend Service unchanged

#### Scenario: Admin Service is internal and h2c with a health check

- **WHEN** the admin backend Service is provisioned
- **THEN** it SHALL be ClusterIP (reachable only via the gateway), advertise h2c via
  `appProtocol`, and be covered by a gRPC `HealthCheckPolicy`

### Requirement: Admin console resolves the admin API host from runtime config

The admin console SHALL obtain the admin API base URL from its per-host runtime
configuration and direct its admin RPC client (the admin
`liverty_music.rpc.admin.v1.ConcertService`) to `api.admin.{env-base-domain}`. The
consumer SPA SHALL continue to call the consumer API host. Neither app SHALL
conditionally rewrite the other's host.

#### Scenario: Admin client targets the admin API host

- **WHEN** the admin console boots and reads its runtime config
- **THEN** its admin RPC client base URL SHALL be the admin API host for that environment

#### Scenario: Consumer client unchanged

- **WHEN** the consumer SPA boots
- **THEN** its RPC client SHALL continue to target the consumer API host

