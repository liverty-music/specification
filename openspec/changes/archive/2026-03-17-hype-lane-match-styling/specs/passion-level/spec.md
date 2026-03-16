## MODIFIED Requirements

### Requirement: Hype Visual Indicators on Dashboard Cards

The system SHALL visually distinguish dashboard event cards based on whether the artist's hype level covers the concert's lane proximity (hype-lane match), rather than on hype level alone. A card is "matched" when the artist's hype radius includes the concert's lane, and "unmatched" otherwise. Matched cards SHALL evoke a live festival stage; unmatched cards SHALL evoke a faded concert poster.

The match truth table:
- **watch**: never matched (any lane)
- **home**: matched on HOME STAGE only
- **nearby**: matched on HOME STAGE and NEAR STAGE
- **away**: matched on HOME STAGE, NEAR STAGE, and AWAY STAGE

#### Scenario: Match computation is TypeScript responsibility

- **WHEN** the system builds a `LiveEvent` from concert data
- **THEN** the match result SHALL be computed in TypeScript as a pure function comparing hype level and lane
- **AND** the result SHALL be exposed as a boolean `matched` property on the `LiveEvent` interface
- **AND** the HTML template SHALL bind `data-matched` attribute from this property
- **AND** CSS SHALL NOT contain hype-lane comparison logic

#### Scenario: Matched card background

- **WHEN** an event card is rendered with `matched = true`
- **THEN** the card background SHALL use a radial-gradient spotlight effect using the artist-color at elevated saturation (oklch chroma 0.20), brighter at an off-center focal point and darker at the edges
- **AND** the card SHALL have a `2px solid` border using the artist's color at 40% opacity
- **AND** the card SHALL have a dual-layer glow: outer `box-shadow: 0 0 16px` at 50% opacity and inner `inset 0 0 12px` at 15% opacity
- **AND** the card background SHALL be clean (no overlay texture)

#### Scenario: Matched card clearLOGO neon glow

- **WHEN** a matched event card has a clearLOGO image (transparent PNG)
- **THEN** the logo SHALL be rendered as an `<img>` element
- **AND** the logo SHALL have a multi-layer `filter: drop-shadow()` neon glow using the artist-color, producing a contour-following glow around the exact logo shape

#### Scenario: Matched card text fallback neon glow

- **WHEN** a matched event card does not have a clearLOGO image
- **THEN** the artist name SHALL be rendered as a text `<span>` element
- **AND** the artist name SHALL have a multi-layer `text-shadow` neon glow using the artist-color

#### Scenario: Matched card spotlight beam cone

- **WHEN** a matched event card is rendered
- **THEN** a vertical light beam cone SHALL illuminate the card from above via a `::before` pseudo-element
- **AND** the beam SHALL use a `linear-gradient` (bright at top, transparent at bottom) shaped by a `mask-image: radial-gradient(ellipse)` to form a narrow cone
- **AND** a bright contact flash (`::after`) SHALL pulse at the card's top edge where the beam hits, using `box-shadow` layers
- **AND** the pseudo-elements SHALL be clipped by `overflow: hidden` on the card

#### Scenario: Matched card color drift animation

- **WHEN** a matched event card is rendered
- **THEN** the artist-color hue SHALL oscillate ±30 degrees over an 8-second ease-in-out infinite cycle via `@property --hue-drift`
- **AND** the hue drift SHALL affect all artist-color references simultaneously (background, border, glow, logo drop-shadow / text-shadow)

#### Scenario: Unmatched card styling

- **WHEN** an event card is rendered with `matched = false`
- **THEN** the card SHALL use a desaturated artist-color (oklch chroma 0.03) as a flat background-color
- **AND** the card SHALL have a `1px solid` border at `white/5%` opacity
- **AND** the card SHALL NOT have a glow effect
- **AND** the card SHALL display an SVG noise texture overlay at 8% opacity via a `::after` pseudo-element
- **AND** the card SHALL NOT have any animations

#### Scenario: Unmatched card clearLOGO dimming

- **WHEN** an unmatched event card has a clearLOGO image
- **THEN** the logo SHALL be rendered with `filter: brightness(0.35) grayscale(0.8)`, appearing dim and desaturated

#### Scenario: Unmatched card text fallback dimming

- **WHEN** an unmatched event card does not have a clearLOGO image
- **THEN** the artist name text SHALL have no text-shadow and reduced opacity

#### Scenario: Away artist matched on all stages

- **GIVEN** a user has set an artist's hype to Away (どこでも！)
- **WHEN** that artist's concerts appear on HOME STAGE, NEAR STAGE, and AWAY STAGE
- **THEN** all three cards SHALL render as matched (spotlight, neon glow, color drift)

#### Scenario: Home artist matched only on home stage

- **GIVEN** a user has set an artist's hype to Home (地元)
- **WHEN** that artist's concerts appear on HOME STAGE and AWAY STAGE
- **THEN** the HOME STAGE card SHALL render as matched
- **AND** the AWAY STAGE card SHALL render as unmatched (desaturated, no glow, noise texture)

#### Scenario: Watch artist always unmatched

- **GIVEN** a user has set an artist's hype to Watch (チェック)
- **WHEN** that artist's concerts appear on any stage
- **THEN** all cards SHALL render as unmatched

#### Scenario: Artist color source

- **WHEN** computing visual effects for a matched or unmatched event card
- **THEN** the artist color SHALL be derived from the existing deterministic color generator (`color-generator.ts`)

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the spotlight sweep animation SHALL be disabled
- **AND** the color drift animation SHALL be disabled
- **AND** static matched effects SHALL remain fully visible (radial-gradient background at center position, border, dual glow, neon logo/text glow)
- **AND** unmatched styling SHALL be unaffected (already static)

#### Scenario: Color drift graceful degradation

- **WHEN** the browser does not support `@property` syntax
- **THEN** the `--hue-drift` value SHALL remain at its initial value of 0
- **AND** all other matched effects (spotlight, glow, border, saturation) SHALL render normally with the static artist-color

## REMOVED Requirements

### Requirement: WATCH card styling
**Reason**: Replaced by hype-lane match model. Watch-level styling is now handled by the unmatched treatment.
**Migration**: Remove `[data-hype="watch"]` CSS selector. Watch artists use `:not([data-matched])` styling.

### Requirement: HOME card styling
**Reason**: Replaced by hype-lane match model. Per-tier visual escalation is removed.
**Migration**: Remove `[data-hype="home"]` CSS selector. Home artists use matched/unmatched styling based on lane.

### Requirement: NEARBY hype card styling
**Reason**: Replaced by hype-lane match model. Per-tier visual escalation is removed.
**Migration**: Remove `[data-hype="nearby"]` CSS selector. Nearby artists use matched/unmatched styling based on lane.

### Requirement: AWAY card styling
**Reason**: Replaced by hype-lane match model. Per-tier visual escalation is removed.
**Migration**: Remove `[data-hype="away"]` CSS selector. Away artists use matched/unmatched styling based on lane.
