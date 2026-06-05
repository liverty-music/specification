## ADDED Requirements

### Requirement: parseStep1Envelope Preserves Tour Grouping On EventDraft

`parseStep1Envelope` SHALL preserve the tour grouping expressed by the Step 1 envelope rather than discarding it during flattening. Each `EventDraft` SHALL carry whether it originated from a `<tour>` or `<standalone>` block, and for tour-origin drafts an **intra-run group handle** that ties together all drafts belonging to the same `<tour>` block. The handle only needs to be unique and stable **within a single parse**; it is NOT a cross-run series key and SHALL NOT be required to derive from `source_url` or title. The existing verbatim fields (`Title`, `SourceURL`, `Venue`, `Country`, `LocalDate`, `StartTime`, `OpenTime`) and the Step-2 merge-by-`index` behavior SHALL be unchanged.

#### Scenario: Tour block drafts share a group handle

- **WHEN** a `<tour>` block with three `<event>` children is parsed
- **THEN** the three resulting `EventDraft`s SHALL each be marked as tour-origin
- **AND** the three SHALL carry the same intra-run group handle

#### Scenario: Standalone drafts are marked standalone

- **WHEN** a `<standalone>` block is parsed
- **THEN** its `EventDraft` SHALL be marked as standalone-origin
- **AND** it SHALL NOT share a tour-group handle with any other draft

#### Scenario: Two distinct tours produce two group handles

- **WHEN** the envelope contains two separate `<tour>` blocks
- **THEN** drafts from the first tour SHALL share one group handle
- **AND** drafts from the second tour SHALL share a different group handle
