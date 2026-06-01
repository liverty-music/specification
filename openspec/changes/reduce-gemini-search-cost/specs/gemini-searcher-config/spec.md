## ADDED Requirements

### Requirement: Configurable search-cache TTL with env-var precedence over default

The job configuration SHALL expose an environment-configurable search-cache TTL that controls how long a completed search is considered fresh. The value SHALL be resolvable from an environment variable (e.g. `GCP_GEMINI_SEARCH_CACHE_TTL`) and SHALL fall back to a built-in default of 24 hours when unset, following the same env-precedence-over-default pattern as the per-step model resolvers. The resolved TTL SHALL be passed into the concert-search use case instead of a hard-coded constant.

#### Scenario: Env override honoured

- **WHEN** the search-cache TTL env var is set to `72h`
- **THEN** the resolved TTL SHALL be 72 hours

#### Scenario: Default applied when env unset

- **WHEN** the search-cache TTL env var is empty or unset
- **THEN** the resolved TTL SHALL be 24 hours

#### Scenario: Invalid value rejected at startup

- **WHEN** the search-cache TTL env var is set to a non-parseable duration
- **THEN** configuration validation SHALL fail fast at job startup with a descriptive error

#### Scenario: No hard-coded freshness constant remains in the use case

- **WHEN** the concert-search use case evaluates search freshness
- **THEN** it SHALL use the configured TTL value
- **AND** the codebase SHALL NOT contain a `searchCacheTTL` constant used as the freshness window

### Requirement: Configurable discovery-skip window with env-var precedence over default

The job configuration SHALL expose an environment-configurable discovery-skip window that controls how long after a successful discovery the external search is skipped. The value SHALL be resolvable from an environment variable (e.g. `GCP_GEMINI_SEARCH_DISCOVERY_WINDOW`) and SHALL fall back to a built-in default of 14 days (336 hours) when unset, following the same env-precedence-over-default pattern as the TTL and the per-step model resolvers. The resolved window SHALL be passed into the concert-search use case.

#### Scenario: Env override honoured

- **WHEN** the discovery-window env var is set to `168h`
- **THEN** the resolved window SHALL be 168 hours (7 days)

#### Scenario: Default applied when env unset

- **WHEN** the discovery-window env var is empty or unset
- **THEN** the resolved window SHALL be 14 days (336 hours)

#### Scenario: Invalid value rejected at startup

- **WHEN** the discovery-window env var is set to a non-parseable duration
- **THEN** configuration validation SHALL fail fast at job startup with a descriptive error

#### Scenario: No hard-coded discovery-window constant remains in the use case

- **WHEN** the concert-search use case evaluates discovery recency
- **THEN** it SHALL use the configured discovery-window value rather than a hard-coded constant
