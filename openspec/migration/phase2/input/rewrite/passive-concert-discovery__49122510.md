<!-- spec: passive-concert-discovery | target: components/infrastructure/fan/web/route/dashboard | flags: CLASSNAME | new_name: All Nearby Concert List -->

### Requirement: All Nearby Concert List

The All Nearby mode SHALL display concerts returned by `ConcertService.ListByLocation` using the existing `ConcertHighway` component with HOME and NEARBY lanes.

#### Scenario: HOME and NEARBY lanes rendered

- **WHEN** `ListByLocation` returns `ProximityGroup[]`
- **THEN** the `ConcertHighway` SHALL render HOME-tier concerts in the HOME lane and NEARBY-tier concerts in the NEARBY lane
- **AND** AWAY-tier concerts SHALL NOT be displayed

#### Scenario: Venue name shown for all lanes

- **WHEN** a concert card is rendered in the All Nearby list
- **THEN** the `listed_venue_name` (or resolved venue name) SHALL be shown regardless of the lane (HOME or NEARBY)
- **AND** this overrides the current Dashboard behavior where HOME-lane cards suppress the venue label

#### Scenario: Empty state

- **WHEN** `ListByLocation` returns an empty `groups` list
- **THEN** the Dashboard SHALL display an empty-state message explaining that no concerts were found for the selected area and date range
- **AND** the empty state SHALL include a link or button navigating to the Discovery tab

---
