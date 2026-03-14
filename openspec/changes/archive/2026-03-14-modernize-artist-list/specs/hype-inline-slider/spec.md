## MODIFIED Requirements

### Requirement: Sticky Header Legend

The My Artists list view SHALL display a sticky header row showing hype tier icons and emotion-based labels, aligned with slider stop positions using a shared grid column definition.

#### Scenario: Header renders with 4 columns

- **WHEN** the My Artists page renders in list view
- **THEN** the system SHALL display a sticky header row below the page title
- **AND** the header SHALL contain 4 equally-spaced columns: 👀 チェック, 🔥 地元, 🔥🔥 近くも, 🔥🔥🔥 どこでも！
- **AND** the header SHALL use `position: sticky; inset-block-start: 0` with `backdrop-filter: blur(8px)` on the surface-raised background
- **AND** each column SHALL vertically align with the corresponding dot stop on artist row sliders
- **AND** the header and artist row content SHALL share the same `grid-template-columns: 2fr repeat(4, 1fr)` definition with `grid-template-areas` to ensure column alignment

#### Scenario: Header column alignment matches artist row dot positions

- **WHEN** the header and any artist row are visible simultaneously
- **THEN** the center of each header label SHALL be horizontally aligned with the center of the corresponding dot in the artist row slider
- **AND** this alignment SHALL be achieved by both elements using `grid-template-columns: 2fr repeat(4, 1fr)` at the same parent width

#### Scenario: Header remains visible during scroll

- **WHEN** the user scrolls the artist list
- **THEN** the sticky header SHALL remain visible at the top of the scroll container
- **AND** the header SHALL have a `[data-hype-header]` attribute for coach mark targeting

### Requirement: Slider dot positions align with header columns

The 4 slider dot stops SHALL be positioned to vertically align with the 4 header legend columns using a shared CSS Grid column template.

#### Scenario: Slider spans header dot columns

- **WHEN** the page renders
- **THEN** the hype-inline-slider component SHALL span grid columns 2 through 5 of the artist row content grid
- **AND** the slider's internal `repeat(4, 1fr)` grid SHALL subdivide the same width as the header's 4 dot columns
- **AND** alignment SHALL be maintained across viewport widths
