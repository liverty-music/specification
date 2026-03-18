## Purpose

This capability defines how artist logos and text fallback names are presented within event cards, ensuring legibility, proper sizing, and alignment regardless of matched/unmatched state.

## Requirements

### Requirement: Logo and text visibility on unmatched cards
Event cards that are not matched SHALL display artist logos and text at full visibility. No dimming filters (brightness, grayscale) SHALL be applied to logos, and no opacity reduction SHALL be applied to text fallback names on unmatched cards.

#### Scenario: Unmatched card with logo
- **WHEN** an unmatched event card displays an artist ClearLOGO image
- **THEN** the logo SHALL render without brightness or grayscale filters

#### Scenario: Unmatched card with text fallback
- **WHEN** an unmatched event card displays an artist name as text (no logo available)
- **THEN** the text SHALL render at full opacity (no opacity reduction)

### Requirement: Center-aligned card content
Artist logos and text fallback names SHALL be horizontally centered within event cards.

#### Scenario: Logo centered in card
- **WHEN** an event card displays a ClearLOGO image
- **THEN** the logo SHALL be horizontally centered within the card

#### Scenario: Text fallback centered in card
- **WHEN** an event card displays an artist name as text
- **THEN** the text SHALL be horizontally centered within the card

### Requirement: Text fallback font size prominence
Artist names displayed as text fallback SHALL be visually prominent and clearly distinguishable from the location label below. The text fallback font size SHALL be larger than the current sizing to provide visual weight comparable to ClearLOGO images.

#### Scenario: Text fallback versus location label
- **WHEN** an event card displays an artist name as text with a location label below
- **THEN** the artist name font size SHALL be noticeably larger than the location label font size

### Requirement: Logo scales to fill card space
Artist ClearLOGO images SHALL scale proportionally to the lane container width using cqi units. The logo SHALL NOT be constrained to a fixed small height.

#### Scenario: Logo fills card height
- **WHEN** an event card displays a ClearLOGO image
- **THEN** the logo SHALL expand proportionally to the lane width, maintaining aspect ratio via `object-fit: contain`
