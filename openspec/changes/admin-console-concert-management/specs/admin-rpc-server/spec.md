## MODIFIED Requirements

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
