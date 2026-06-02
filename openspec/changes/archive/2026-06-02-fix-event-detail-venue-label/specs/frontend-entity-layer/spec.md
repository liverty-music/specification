## ADDED Requirements

### Requirement: Concert region is presentation-ready

The presentation `Concert` entity SHALL expose the venue's administrative area only as a human-readable, localized display label (`locationLabel`). It SHALL NOT carry the raw ISO 3166-2 subdivision code. The adapter layer (`concert-mapper.ts`) is the single point that translates the proto `venue.admin_area` code into the display label; presentation code SHALL consume `locationLabel` and SHALL NOT re-derive the label from a raw code.

#### Scenario: Mapper produces only the display label

- **WHEN** the RPC mapper maps a proto `Concert` whose `venue.admin_area` is a known code (e.g. `JP-13`)
- **THEN** the resulting entity SHALL set `locationLabel` to the localized name (e.g. `東京都`)
- **AND** the entity SHALL NOT expose the raw `JP-13` code

#### Scenario: Missing admin area yields empty label

- **WHEN** the proto `Concert` has no `venue.admin_area`
- **THEN** the entity's `locationLabel` SHALL be an empty string
- **AND** consumers SHALL treat the empty string as "no administrative area to display"

#### Scenario: Presentation consumes the label, not a code

- **WHEN** a component needs the administrative area for display or for composing a derived value (e.g. a Google Maps query)
- **THEN** it SHALL read `locationLabel`
- **AND** it SHALL NOT call the code-to-name normalization helper to re-derive the label
