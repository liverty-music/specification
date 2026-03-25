## ADDED Requirements

### Requirement: ConcertService handler timeout isolation
The ConcertService RPC handlers SHALL have a dedicated handler timeout of 120 seconds, separate from the default handler timeout applied to other services. This accommodates the Gemini API + Google Search grounding response time (25-110 seconds).

#### Scenario: SearchNewConcerts completes within 120 seconds
- **WHEN** `SearchNewConcerts` is called and the Gemini API responds within 120 seconds
- **THEN** the RPC SHALL return successfully with discovered concerts

#### Scenario: SearchNewConcerts exceeds 120 seconds
- **WHEN** `SearchNewConcerts` is called and the handler timeout of 120 seconds is exceeded
- **THEN** the RPC SHALL return a deadline exceeded error to the client

#### Scenario: Other services retain default timeout
- **WHEN** an RPC on UserService or ArtistService is called
- **THEN** the default handler timeout (60 seconds) SHALL apply
- **AND** the ConcertService timeout SHALL NOT affect other services

### Requirement: GKE Gateway timeout for ConcertService
The GKE Gateway backend policy `timeoutSec` SHALL be set to 150 seconds to accommodate the ConcertService handler timeout (120 seconds) plus network overhead buffer.

#### Scenario: Gateway timeout exceeds handler timeout
- **WHEN** a request is routed through the GKE Gateway to the backend
- **THEN** the Gateway timeout (150 seconds) SHALL be greater than the ConcertService handler timeout (120 seconds)
- **AND** the Gateway SHALL NOT prematurely terminate ConcertService requests
