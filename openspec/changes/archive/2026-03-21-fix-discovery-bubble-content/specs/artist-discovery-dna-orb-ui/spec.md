## ADDED Requirements

### Requirement: Bubble Content Display

Each bubble SHALL display the artist's name as its sole visual content, centered within the bubble area. No images SHALL be loaded or rendered inside bubbles.

#### Scenario: Artist name centered in bubble

- **WHEN** artist bubbles are rendered on the canvas
- **THEN** each bubble SHALL display the artist's name centered horizontally and vertically within the bubble
- **AND** the bubble SHALL NOT load or display any image (no fanart, no logo, no thumbnail)

#### Scenario: Font size adapts to name length

- **WHEN** the artist's name is rendered inside a bubble
- **THEN** the font size SHALL scale based on the bubble radius (base size proportional to radius)
- **AND** if the rendered text width exceeds the available bubble diameter, the font size SHALL be reduced to fit

#### Scenario: Long names wrap to multiple lines

- **WHEN** the artist's name contains multiple words and the full name exceeds the bubble width at the current font size
- **THEN** the name SHALL wrap to multiple lines using word boundaries
- **AND** all lines SHALL be vertically centered as a group within the bubble
- **AND** each line SHALL be horizontally centered
