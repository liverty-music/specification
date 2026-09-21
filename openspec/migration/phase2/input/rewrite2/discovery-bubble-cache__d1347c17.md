<!-- spec: discovery-bubble-cache | target: components/infrastructure/fan/web/route/discovery | flags: THRESHOLD | new_name: Re-entry preserves the in-session bubble field -->
<!-- THRESHOLD: 'display floor' = 30 bubbles; 'cache TTL' = 15 minutes (measured from code) -->

### Requirement: Re-entry preserves the in-session bubble field
Within a session, navigating away from Discovery and back SHALL preserve the field the user was viewing rather than re-deriving it. When the cached field is fresh (within its TTL), the system SHALL reuse it and apply only a non-destructive delta; it SHALL NOT issue a wholesale `replace()` that recomposes the field or reduces it below the display floor.

#### Scenario: Fresh field is reused on re-entry
- **WHEN** the user returns to Discovery within the cache TTL
- **THEN** the previously displayed field SHALL be reused as the starting field
- **AND** the rendered bubble count SHALL NOT drop below the count shown before leaving, except for artists the user followed while away

#### Scenario: Non-destructive delta on refresh
- **WHEN** a background refresh runs on re-entry
- **THEN** it SHALL remove only newly-followed artists and top up only if the field is below the display floor
- **AND** it SHALL NOT replace the entire field with a freshly-fetched set that changes composition or shrinks the field

#### Scenario: Follow while away is reconciled without collapsing the field
- **WHEN** the user followed one or more artists on another route and returns to Discovery
- **THEN** only the newly-followed artists SHALL be removed from the field
- **AND** the remaining bubbles SHALL stay, with top-up applied only to restore the display floor

#### Scenario: Stale field triggers a full reload
- **WHEN** the user returns to Discovery after the cache TTL has expired
- **THEN** the system MAY perform a full reload as on a cold visit
- **AND** the reload SHALL still converge to a field within capacity with render parity
