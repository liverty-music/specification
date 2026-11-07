## MODIFIED Requirements

### Requirement: The ticket section shows the four statuses in one row

The concert detail sheet's ticket section SHALL show the ticket sale notification button on its own full-width row and the other four statuses as one row of compact buttons in journey order, 📝 申込済み › 💰 当選・未入金 › 🎟️ 入金済み, followed by 💔 落選 set apart by a separator. The row SHALL keep every status's canonical label, icon and hue, wrap rather than overflow on a narrow screen, and give each button a tap target of at least 48px.

#### Scenario: One row for four statuses

- **WHEN** the ticket section is displayed for a signed-in fan on a 390px-wide screen
- **THEN** the four status buttons are laid out in one row in journey order, with 落選 after a separator
- **AND** the `›` connectors sit between 申込済み, 当選・未入金 and 入金済み

#### Scenario: Narrow viewport does not overflow

- **WHEN** the row cannot fit on one line
- **THEN** the row wraps rather than overflowing horizontally

#### Scenario: Canonical presentation kept

- **WHEN** any status button is rendered
- **THEN** its label, icon and hue come from the canonical journey-status presentation map, and its tap target is at least 48px
