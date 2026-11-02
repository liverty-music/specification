## ADDED Requirements

### Requirement: Dashboard cards show whether the hype level matches the concert

The system SHALL visually distinguish dashboard event cards based on whether the artist's hype level matches the concert by its lane, rather than on hype level alone. A card is "matched" when the artist's hype level matches the concert's lane, and "unmatched" otherwise. A matched card SHALL look lit like a festival stage; an unmatched card SHALL show the artist's color without light effects.

The match truth table:
- **watch**: never matched (any lane)
- **home**: matched on HOME STAGE only
- **nearby**: matched on HOME STAGE and NEAR STAGE
- **away**: matched on HOME STAGE, NEAR STAGE, and AWAY STAGE

#### Scenario: Match computation is application-code responsibility

- **WHEN** the system builds the data used to render a dashboard event card
- **THEN** the match result SHALL be computed as a pure function comparing hype level and lane
- **AND** the result SHALL be exposed as a matched/unmatched state on the card's data
- **AND** the card's template SHALL bind a `data-matched` attribute from this state
- **AND** CSS SHALL NOT contain hype-lane comparison logic

#### Scenario: Matched card is lit like a stage

- **WHEN** a matched event card is rendered
- **THEN** the card SHALL fill with a diagonal gradient of the artist's color, from the artist's hue to that hue turned by 40 degrees
- **AND** the card SHALL have a 2px border in a bright tint of the artist's color
- **AND** the card SHALL glow in the artist's color around its edges and inward from its top edge

#### Scenario: Matched card has a light beam from above

- **WHEN** a matched event card is rendered
- **THEN** a narrow beam of light in the artist's color SHALL fall from the center of the card's top edge, brightest at the top and faded out before 70% of the card's height
- **AND** the beam SHALL stay inside the card

#### Scenario: Matched card artist name glows

- **WHEN** a matched event card is rendered
- **THEN** the artist name SHALL glow in the artist's color

#### Scenario: Unmatched card shows the artist's color without light

- **WHEN** an unmatched event card is rendered
- **THEN** the card SHALL fill with the same diagonal gradient of the artist's color as a matched card, at a lighter shade
- **AND** the card SHALL have a 1px border in white at 12% opacity
- **AND** the card SHALL show a fine grain texture at 8% opacity over its background
- **AND** the card SHALL have no glow, no light beam, and no glow on the artist name

#### Scenario: Away artist matched on all stages

- **GIVEN** a user has set an artist's hype to Away (どこでも！)
- **WHEN** that artist's concerts appear on HOME STAGE, NEAR STAGE, and AWAY STAGE
- **THEN** all three cards SHALL render as matched (lit like a stage, with a light beam and a glowing artist name)

#### Scenario: Home artist matched only on home stage

- **GIVEN** a user has set an artist's hype to Home (地元)
- **WHEN** that artist's concerts appear on HOME STAGE and AWAY STAGE
- **THEN** the HOME STAGE card SHALL render as matched
- **AND** the AWAY STAGE card SHALL render as unmatched (no glow, no light beam, grain texture)

#### Scenario: Watch artist always unmatched

- **GIVEN** a user has set an artist's hype to Watch (チェック)
- **WHEN** that artist's concerts appear on any stage
- **THEN** all cards SHALL render as unmatched

#### Scenario: Artist color source

- **WHEN** computing visual effects for a matched or unmatched event card
- **THEN** the artist color SHALL be derived from the existing deterministic color generation logic

#### Scenario: Card treatments hold still

- **WHEN** a matched or unmatched event card is on screen, whether or not the fan prefers reduced motion
- **THEN** no part of the card's matched or unmatched treatment SHALL animate
- **AND** the treatment SHALL look the same with reduced motion as without it

### Requirement: Artist name shown on every card

Every dashboard event card SHALL show the artist's name as text, horizontally centered on the card, in white at full opacity on matched and unmatched cards alike. A card SHALL NOT show the artist's logo image.

#### Scenario: Artist name centered on the card

- **WHEN** an event card is rendered
- **THEN** the artist's name SHALL be shown as text, horizontally centered on the card

#### Scenario: Unmatched card name at full visibility

- **WHEN** an unmatched event card is rendered
- **THEN** the artist's name SHALL render in white with no opacity reduction or dimming filter

## MODIFIED Requirements

### Requirement: Text fallback font size prominence
The artist name on an event card SHALL be visually prominent and clearly distinguishable from the location label below it: its font size SHALL be larger than the location label's.

#### Scenario: Text fallback versus location label
- **WHEN** an event card displays an artist name with a location label below
- **THEN** the artist name font size SHALL be noticeably larger than the location label font size

## REMOVED Requirements

### Requirement: Hype Visual Indicators on Dashboard Cards
**Reason**: Replaced by "Dashboard cards show whether the hype level matches the concert", which uses the entity term "matches" and describes the cards as the app renders them: the card shows no artist logo, the matched card's color no longer drifts, and the unmatched card shows a lighter gradient with grain instead of a desaturated, dimmed poster.
**Migration**: None.

### Requirement: Event Card Logo Display
**Reason**: Event cards show the artist's name as text on every card and never a logo image (replaced by "Artist name shown on every card").
**Migration**: None.

### Requirement: Logo and text visibility on unmatched cards
**Reason**: Cards show no logo; the full visibility of the artist name on an unmatched card moves to "Artist name shown on every card".
**Migration**: None.

### Requirement: Center-aligned card content
**Reason**: Cards show no logo; centering the artist name moves to "Artist name shown on every card".
**Migration**: None.

### Requirement: Logo scales to fill card space
**Reason**: Event cards show no logo image.
**Migration**: None.
