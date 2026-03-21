## MODIFIED Requirements

### Requirement: Logo scales to fill card space
Artist ClearLOGO images SHALL stretch to fill the full inline size of the card (`inline-size: 100%`) while maintaining aspect ratio via `object-fit: contain`. The logo SHALL NOT be constrained to a percentage of the card width. The existing vertical constraint (`max-block-size: 25cqi`) SHALL be preserved.

#### Scenario: Logo fills card width
- **WHEN** an event card displays a ClearLOGO image
- **THEN** the logo SHALL expand to fill 100% of the card's inline size, maintaining aspect ratio via `object-fit: contain`

#### Scenario: Logo respects vertical constraint
- **WHEN** an event card displays a ClearLOGO image in a tall card
- **THEN** the logo's block size SHALL NOT exceed `25cqi`, even when inline size is 100%

## REMOVED Requirements

### Requirement: Unmatched card dimming
**Reason**: The adaptive contrast background strategy (clamping lightness to 12–30% with chroma 0.03) has been retired. Unmatched cards now use the standard `--artist-color-dim` background like all other cards.
**Migration**: No migration needed. CSS rule `.event-card:not([data-matched])` background-color calculation is replaced with `var(--artist-color-dim)`.
