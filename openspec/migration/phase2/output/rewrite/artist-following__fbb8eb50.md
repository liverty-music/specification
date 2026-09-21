<!-- spec: artist-following | target: components/infrastructure/fan/web/global/artist-filter-bar | flags: CLASSNAME | new_name: Filter sheet initializes selection from followed artists -->

### Requirement: Filter sheet initializes selection from followed artists

When the artist filter sheet is opened, it SHALL initialize its selection from the user's currently followed artists, so the displayed selection reflects the user's actual followed artists.

#### Scenario: No followed artists when the sheet opens

- **GIVEN** the user follows no artists
- **WHEN** the filter sheet is opened
- **THEN** the selection SHALL be initialized to empty

#### Scenario: Multiple followed artists when the sheet opens

- **GIVEN** the user follows multiple artists
- **WHEN** the filter sheet is opened
- **THEN** the selection SHALL be initialized with the IDs of all currently followed artists

#### Scenario: Reopening the sheet resets the selection

- **GIVEN** the sheet has been opened and the selection has since been changed
- **WHEN** the sheet is opened again
- **THEN** the selection SHALL be reset to reflect the current followed artists, discarding any prior changes
