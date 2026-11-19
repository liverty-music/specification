# Spec Delta

## MODIFIED Requirements

### Requirement: The fan page of a published date

For a published date of a PUBLIC concert, the page SHALL show the address of the date's fan concert page (`/concerts/<event id>` on the fan app) with a copy action, so the member can share it. A draft or cancelled date, and any date of an UNLISTED concert, SHALL show no fan address, because fans cannot open it.

#### Scenario: Public date

- **WHEN** a member opens the published 3 November event of the PUBLIC concert XX Tour 2026
- **THEN** the page shows the fan page address of that event, and copying puts it on the clipboard

#### Scenario: Unlisted concert

- **WHEN** a member opens a published event of an UNLISTED concert
- **THEN** no fan page address is shown
