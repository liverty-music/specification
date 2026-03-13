# Capability: Hype Inline Slider

## Purpose

Provide a 1-tap inline slider for setting hype level per artist in the My Artists list view, with a sticky header legend and artist-color glow on the active dot.

## ADDED Requirements

### Requirement: Sticky Header Legend

The My Artists list view SHALL display a sticky header row showing hype tier icons and emotion-based labels, aligned with slider stop positions.

#### Scenario: Header renders with 4 columns

- **WHEN** the My Artists page renders in list view
- **THEN** the system SHALL display a sticky header row below the page title
- **AND** the header SHALL contain 4 equally-spaced columns: 👀 チェック, 🔥 地元, 🔥🔥 近くも, 🔥🔥🔥 どこでも！
- **AND** the header SHALL use `position: sticky; top: 0` with `backdrop-filter: blur(8px)` on the surface-raised background
- **AND** each column SHALL vertically align with the corresponding dot stop on artist row sliders

#### Scenario: Header remains visible during scroll

- **WHEN** the user scrolls the artist list
- **THEN** the sticky header SHALL remain visible at the top of the scroll container
- **AND** the header SHALL have a `[data-hype-header]` attribute for coach mark targeting

### Requirement: Inline Dot Slider

Each artist row in the My Artists list view SHALL include a 4-stop discrete dot slider for hype level selection, enabling 1-tap changes without opening a bottom sheet.

#### Scenario: Slider renders on each artist row

- **WHEN** an artist row renders in list view
- **THEN** the row SHALL display the artist name (left-aligned, truncated with ellipsis) and the dot slider (right-aligned) on the same row
- **AND** the slider SHALL display 4 dot stops connected by a 2px track line
- **AND** the active dot SHALL be 14px diameter; inactive dots SHALL be 8px diameter
- **AND** each dot SHALL have a minimum 44×44px transparent tap target area

#### Scenario: Active dot reflects hype tier CSS effects

- **WHEN** the slider renders with a specific hype level selected
- **THEN** the active dot SHALL apply the same CSS glow effects as defined in the passion-level card styling spec:
  - WATCH: `1px solid white/10` border, no glow
  - HOME: artist-color border at 40% opacity, `box-shadow: 0 0 8px` at 30% opacity
  - NEARBY: artist-color `2px solid` border, `box-shadow: 0 0 16px` at 50% opacity, gentle pulse animation
  - AWAY: animated gradient border, layered glow (`0 0 24px` at 60% + `0 0 48px` at 20%), strong pulse animation
- **AND** the artist color SHALL be derived from the existing deterministic color generator

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** all pulse and gradient rotation animations on active dots SHALL be disabled
- **AND** static border and glow styles SHALL remain visible

#### Scenario: Authenticated user taps a dot

- **WHEN** an authenticated user taps an inactive dot on a slider
- **THEN** the active dot SHALL animate to the tapped position (200ms ease-out transition)
- **AND** the system SHALL optimistically update the UI
- **AND** the system SHALL call `SetHype` RPC with the new hype level
- **AND** if the RPC fails, the slider SHALL revert to the previous position

#### Scenario: Unauthenticated user taps a dot

- **WHEN** an unauthenticated user taps any dot on a slider
- **THEN** the slider SHALL NOT move
- **AND** the system SHALL dispatch a `hype-signup-prompt` custom event
- **AND** the My Artists page SHALL handle this event by displaying the notification dialog (see `onboarding-tutorial` spec)

#### Scenario: Slider dot positions align with header columns

- **WHEN** the page renders
- **THEN** the 4 slider dot stops SHALL be positioned to vertically align with the 4 header legend columns
- **AND** alignment SHALL be maintained across viewport widths (CSS Grid shared column template)
