## ADDED Requirements

### Requirement: Hype Visual Indicators on Dashboard Cards

The system SHALL visually indicate hype (passion) levels on dashboard event cards using border gradient, glow effects, and neon text-shadow, without consuming additional card space.

#### Scenario: WATCH (Keep an Eye) card styling

- **WHEN** an event card is rendered for an artist with Keep an Eye hype level
- **THEN** the card SHALL have a `1px solid` border at `white/10` opacity
- **AND** the card SHALL NOT have glow or text-shadow effects
- **AND** no emoji badge SHALL be displayed

#### Scenario: HOME (Local Only) card styling

- **WHEN** an event card is rendered for an artist with Local Only hype level
- **THEN** the card SHALL have a `1px solid` border using the artist's color at 40% opacity
- **AND** the card SHALL have a subtle `box-shadow: 0 0 8px` glow using the artist's color at 30% opacity
- **AND** the artist name SHALL have a subtle `text-shadow: 0 0 4px` using the artist's color at 30% opacity
- **AND** no emoji badge SHALL be displayed

#### Scenario: NEARBY hype card styling

- **WHEN** an event card is rendered for an artist with Nearby hype level
- **THEN** the card SHALL have a `2px solid` border using the artist's color
- **AND** the card SHALL have a `box-shadow: 0 0 16px` glow using the artist's color at 50% opacity
- **AND** the artist name SHALL have a `text-shadow: 0 0 8px` neon effect using the artist's color at 60% opacity
- **AND** the glow SHALL animate with a gentle pulse (2-second cycle)
- **AND** no emoji badge SHALL be displayed

#### Scenario: AWAY (Must Go) card styling

- **WHEN** an event card is rendered for an artist with Must Go (Away) hype level
- **THEN** the card SHALL have a `2px` animated gradient border (conic-gradient rotation)
- **AND** the card SHALL have a layered glow: `box-shadow: 0 0 24px` at 60% opacity and `0 0 48px` at 20% opacity
- **AND** the artist name SHALL have a strong neon `text-shadow: 0 0 12px` and `0 0 24px` at 40% opacity
- **AND** the glow and gradient SHALL animate with a strong pulse (1.5-second cycle)
- **AND** no emoji badge SHALL be displayed

#### Scenario: Artist color source

- **WHEN** computing hype visual effects for an event card
- **THEN** the artist color SHALL be derived from the existing deterministic color generator (`color-generator.ts`)

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** all pulse and gradient rotation animations SHALL be disabled
- **AND** static border and glow styles SHALL remain visible
- **AND** text-shadow neon effects SHALL remain visible (they are static)

## REMOVED Requirements

### Requirement: Emoji badge hype indicators on event cards

**Reason**: Emoji badges (👀, 🔥, 🔥🔥, 🔥🔥🔥) overlap artist names in narrow lanes and consume card space. Replaced by zero-space border/glow/neon system.
**Migration**: Remove emoji badge elements from event card templates. Remove `HYPE_META` icon references from event card rendering. Hype visualization is now handled entirely via CSS classes based on hype level.
