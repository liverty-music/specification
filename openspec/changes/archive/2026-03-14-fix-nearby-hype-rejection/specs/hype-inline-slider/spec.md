## MODIFIED Requirements

### Requirement: Inline Dot Slider

Each artist row in the My Artists list view SHALL include a 4-stop discrete dot slider for hype level selection, enabling 1-tap changes without opening a bottom sheet.

The frontend hype constants SHALL use a unified naming convention prefixed with `HYPE_`:

| Constant | Purpose |
|----------|---------|
| `HYPE_TIERS` | Tier metadata (label, icon) keyed by HypeType enum |
| `HYPE_TO_STOP` | HypeType enum → slider stop string |
| `HYPE_FROM_STOP` | Slider stop string → HypeType enum |

#### Scenario: Slider renders on each artist row

- **WHEN** an artist row renders in list view
- **THEN** the row SHALL display the artist name (left-aligned, truncated with ellipsis) and the dot slider (right-aligned) on the same row
- **AND** the slider SHALL display 4 dot stops connected by a 2px track line
- **AND** the active dot SHALL be 14px diameter; inactive dots SHALL be 8px diameter
- **AND** each dot SHALL have a minimum 44x44px transparent tap target area

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
