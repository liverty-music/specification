## MODIFIED Requirements

### Requirement: Inline Dot Slider

Each artist row in the My Artists list view SHALL include a 4-stop discrete dot slider for hype level selection, enabling 1-tap changes without opening a bottom sheet.

The slider component SHALL accept `HypeType` enum values directly from the parent binding. No intermediate string type conversion SHALL exist in the parent route.

The slider SHALL use native HTML `<fieldset>` with a visually hidden `<legend>` as the group container. Each hype stop SHALL be a `<label>` wrapping a native `<input type="radio">` (visually hidden) and a visual dot `<span>`. The radio inputs SHALL use Aurelia 2's `model.bind`/`checked.bind` pattern for two-way binding.

#### Scenario: Slider renders on each artist row

- **WHEN** an artist row renders in list view
- **THEN** the row SHALL display the artist name (left-aligned, truncated with ellipsis) and the dot slider (right-aligned) on the same row
- **AND** the slider SHALL display 4 dot stops connected by a 2px track line
- **AND** the active dot SHALL be 14px diameter; inactive dots SHALL be 8px diameter
- **AND** each dot SHALL have a minimum 44x44px transparent tap target area

#### Scenario: Parent binds HypeType directly

- **WHEN** the my-artists-route template renders a `hype-inline-slider`
- **THEN** the binding SHALL be `hype.bind="artist.hype"` using the `HypeType` proto enum
- **AND** the component SHALL NOT require the parent to perform type conversion
- **AND** Aurelia SHALL observe `artist.hype` directly, ensuring optimistic updates are reflected

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

#### Scenario: Authenticated user taps a dot

- **WHEN** an authenticated user taps an inactive dot on a slider
- **THEN** the active dot SHALL animate to the tapped position (200ms ease-out transition)
- **AND** the system SHALL optimistically update `artist.hype` in the parent's artists array
- **AND** the system SHALL call `SetHype` RPC with the new hype level
- **AND** if the RPC fails, the slider SHALL revert to the previous position
- **AND** the `hype-changed` event detail SHALL contain `{ artistId: string, hype: HypeType }`

#### Scenario: Unauthenticated user taps a dot

- **WHEN** an unauthenticated user taps any dot on a slider
- **THEN** the slider SHALL NOT move
- **AND** the system SHALL dispatch a `hype-signup-prompt` custom event
- **AND** the My Artists page SHALL handle this event by displaying the notification dialog

#### Scenario: Native radio input semantics

- **WHEN** the slider renders
- **THEN** the container SHALL be a `<fieldset>` with a visually hidden `<legend>` reading "Hype level"
- **AND** each stop SHALL be a `<label>` containing a visually hidden `<input type="radio">` and a visual dot `<span>`
- **AND** all radio inputs SHALL share a `name` attribute scoped to the artist (e.g., `hype-{artistId}`)
- **AND** the selected radio SHALL be `checked` via Aurelia's `model.bind`/`checked.bind` pattern
- **AND** for unauthenticated users, `click` SHALL be intercepted with `preventDefault()` to block selection

## REMOVED Requirements

### Requirement: HypeStop string constants

**Reason**: The `HYPE_TO_STOP` and `HYPE_FROM_STOP` conversion tables and the `HypeStop` type are replaced by direct `HypeType` enum usage. The indirection added complexity and caused a reactivity bug.

**Migration**: The component accepts `HypeType` directly. Remove `hypeStop()` method and conversion constants from `my-artists-route.ts`. Update event handlers to use `HypeType` instead of `HypeStop`.
