# Capability: Hype Inline Slider

## Purpose

Provide a 1-tap inline slider for setting hype level per artist in the My Artists list view, with a sticky header legend and artist-color glow on the active dot.

## Requirements

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

### Requirement: Inline Dot Slider

Each artist row in the My Artists list view SHALL include a 4-stop discrete dot slider for hype level selection, enabling 1-tap changes without opening a bottom sheet.

The slider component SHALL be a pure presentation component with zero business logic. It SHALL expose `hype` as a `twoWay` bindable and render the active dot accordingly. The slider SHALL NOT contain authentication, onboarding, persistence, or event dispatch logic.

The slider SHALL use native HTML `<fieldset>` with a visually hidden `<legend>` as the group container. Each hype stop SHALL be a `<label>` wrapping a native `<input type="radio">` (visually hidden) and a visual dot `<span>`. The radio inputs SHALL use Aurelia 2's `model.bind`/`checked.bind` pattern with two-way binding on `hype`. When the user taps a dot, the radio's native behavior updates `hype` via Aurelia binding, which pushes to the parent's data via `twoWay` mode. The native `change` event bubbles through the light DOM to the parent, which decides whether to accept or revert the change.

#### Scenario: Slider renders on each artist row

- **WHEN** an artist row renders in list view
- **THEN** the row SHALL display the artist name (left-aligned, truncated with ellipsis) and the dot slider (right-aligned) on the same row
- **AND** the slider SHALL display 4 dot stops connected by a 2px track line
- **AND** the active dot SHALL be 14px diameter; inactive dots SHALL be 8px diameter
- **AND** each dot SHALL have a minimum 44x44px transparent tap target area

#### Scenario: User taps a dot

- **WHEN** a user taps any dot on a slider
- **THEN** the radio's native `checked` state SHALL update via Aurelia's `checked.bind`
- **AND** the `twoWay` binding SHALL push the new value to the parent's bound property
- **AND** the native `change` event SHALL bubble through the custom element boundary
- **AND** the parent SHALL handle the `change` event to apply business logic

#### Scenario: Parent accepts hype selection

- **WHEN** the parent does NOT revert the bound property after a `change` event
- **THEN** the slider SHALL remain at the new position (already updated by native radio behavior)

#### Scenario: Parent reverts hype selection

- **WHEN** the parent reverts the bound property (e.g., `artist.hype = prevValue`) after a `change` event
- **THEN** the `twoWay` binding SHALL push the reverted value back to the slider
- **AND** the slider SHALL return to the previous dot position
- **AND** the programmatic update SHALL NOT trigger another `change` event (native DOM behavior)

#### Scenario: Active dot reflects hype tier CSS effects

- **WHEN** the slider renders with a specific hype level selected
- **THEN** the active dot SHALL apply CSS glow effects based on the `HypeType` enum value:
  - WATCH (1): `1px solid white/10` border, no glow
  - HOME (2): artist-color border at 40% opacity, `box-shadow: 0 0 8px` at 30% opacity
  - NEARBY (3): artist-color `2px solid` border, `box-shadow: 0 0 16px` at 50% opacity, gentle pulse animation
  - AWAY (4): animated gradient border, layered glow (`0 0 24px` at 60% + `0 0 48px` at 20%), strong pulse animation
- **AND** the CSS `data-level` attribute SHALL use `HypeType` enum values (1, 2, 3, 4)
- **AND** the artist color SHALL be derived from the existing deterministic color generator

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** all pulse and gradient rotation animations on active dots SHALL be disabled
- **AND** static border and glow styles SHALL remain visible

#### Scenario: Native radio input semantics

- **WHEN** the slider renders
- **THEN** the container SHALL be a `<fieldset>` with a visually hidden `<legend>` reading "Hype level"
- **AND** each stop SHALL be a `<label>` containing a visually hidden `<input type="radio">` and a visual dot `<span>`
- **AND** all radio inputs SHALL share a `name` attribute scoped to the artist (e.g., `hype-{artistId}`)
- **AND** the selected radio SHALL be `checked` via Aurelia's `model.bind`/`checked.bind` pattern

### Requirement: Slider Track Vertical Centering

The slider track line SHALL be vertically centered within the slider grid cell using CSS logical properties.

#### Scenario: Track is vertically centered

- **WHEN** the slider renders
- **THEN** the `.hype-slider-track` element SHALL use `inset-block-start: 50%` and `translate: 0 -50%` to center vertically within the grid row
- **AND** the track SHALL remain centered across viewport sizes

### Requirement: Slider dot positions align with header columns

The 4 slider dot stops SHALL be positioned to vertically align with the 4 header legend columns using a shared CSS Grid column template.

#### Scenario: Slider spans header dot columns

- **WHEN** the page renders
- **THEN** the hype-inline-slider component SHALL span grid columns 2 through 5 of the artist row content grid
- **AND** the slider's internal `repeat(4, 1fr)` grid SHALL subdivide the same width as the header's 4 dot columns
- **AND** alignment SHALL be maintained across viewport widths
