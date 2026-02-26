## ADDED Requirements

### Requirement: ZK Circuit File Pre-Cache
The system SHALL eagerly cache ZK circuit files (`ticketcheck.wasm` and `ticketcheck.zkey`) during the Service Worker install event to eliminate cold-cache latency on first QR proof generation.

#### Scenario: Service Worker install — circuit files pre-cached
- **WHEN** the Service Worker is installed for the first time (or updated)
- **THEN** the Service Worker SHALL fetch `/ticketcheck.wasm` and `/ticketcheck.zkey` during the `install` event
- **AND** the Service Worker SHALL store both files in the `zk-circuits-v1` cache
- **AND** subsequent requests for these files SHALL be served from cache via the existing CacheFirst route

#### Scenario: Pre-cache fetch fails on slow network
- **WHEN** the circuit file pre-cache fetch fails during SW install (e.g., slow or interrupted network)
- **THEN** the Service Worker SHALL NOT block activation
- **AND** the system SHALL fall back to the existing runtime CacheFirst strategy (fetched on first use)
- **AND** the Service Worker SHALL log a warning to the console

#### Scenario: Circuit files already cached
- **WHEN** the Service Worker is updated but the circuit files are already present in the `zk-circuits-v1` cache
- **THEN** the Service Worker SHALL skip re-fetching the cached files
- **AND** the install event SHALL complete without unnecessary network usage
