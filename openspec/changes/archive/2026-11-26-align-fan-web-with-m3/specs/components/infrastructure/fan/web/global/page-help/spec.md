## ADDED Requirements

### Requirement: The flame count is read out

In the hype tier table of the My Artists help, each tier's flames SHALL be an image named with how many flames there are (for example "炎 2 つ" in Japanese and "2 flames" in English), because the count ranks the tier. The eyes of the Watch tier add nothing to its label and SHALL stay hidden from assistive technology.

#### Scenario: The flame count is read out

- **WHEN** a screen reader reads the hype tier table
- **THEN** the Home, Nearby and Away rows' icons are read as one, two and three flames

## MODIFIED Requirements

### Requirement: Hype tier table is a 3-column grid

The My Artists help sheet's hype tier explanation SHALL render as a list of four rows laid out on one shared 3-column grid, where:
- Column 1 is sized to its widest cell and contains the tier icon (`👀`, `🔥`, `🔥🔥`, `🔥🔥🔥`), centered. The eyes are hidden from assistive technology; each set of flames is an image named with its count.
- Column 2 is sized to its widest cell and contains the invariant English tier label (`Watch`, `Home`, `Nearby`, `Away`), start-aligned.
- Column 3 takes the remaining width and contains the notification-scope description sentence, start-aligned.

#### Scenario: Column alignment

- **WHEN** the My Artists help sheet renders the hype tier explanation
- **THEN** the four rows share three vertical column edges (icon-column right edge, label-column right edge, description-column left edge are each aligned across all rows)
- **AND** the label-column left edge is aligned across all four rows regardless of icon width (`👀` is narrower than `🔥🔥🔥`)
- **AND** the description-column left edge is aligned across all four rows regardless of label width (`Home` is narrower than `Nearby`)

#### Scenario: Tier content per row

- **WHEN** the help sheet renders the hype tier grid
- **THEN** the four rows are (in order, top-to-bottom):
  - `👀` · `Watch` · "通知なし" (JA) / "No notifications" (EN)
  - `🔥` · `Home` · "HOMEエリアのライブを通知" (JA) / "Notify for home-area concerts" (EN)
  - `🔥🔥` · `Nearby` · "近くのライブも通知" (JA) / "Notify for nearby concerts too" (EN)
  - `🔥🔥🔥` · `Away` · "全てのライブを通知" (JA) / "Notify for every concert" (EN)
- **AND** the tier labels in column 2 are the invariant English forms regardless of locale
- **AND** the Away description does not contain the word `全国`

#### Scenario: Semantic markup

- **WHEN** a screen reader reads the hype tier grid
- **THEN** it reads a list of four items, each item giving the tier label and its description
- **AND** it does not read the Watch tier's eyes, and reads each set of flames as its count ("The flame count is read out")
