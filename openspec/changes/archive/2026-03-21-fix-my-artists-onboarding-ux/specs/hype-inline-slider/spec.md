## MODIFIED Requirements

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
- **THEN** the active dot SHALL apply CSS glow effects based on the hype level string:
  - `watch`: `1px solid white/10` border, no glow
  - `home`: artist-color border at 40% opacity, `box-shadow: 0 0 8px` at 30% opacity
  - `nearby`: artist-color `2px solid` border, `box-shadow: 0 0 16px` at 50% opacity, gentle pulse animation
  - `away`: artist-color `2px solid` border, layered glow (`0 0 24px` at 60% + `0 0 48px` at 20%), strong pulse animation
- **AND** the CSS `data-level` attribute SHALL use hype level strings (`watch`, `home`, `nearby`, `away`)
- **AND** the artist color SHALL be derived from the existing deterministic color generator

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** all pulse and gradient rotation animations on active dots SHALL be disabled
- **AND** static border and glow styles SHALL remain visible

#### Scenario: Native radio input semantics

- **WHEN** the artist table renders
- **THEN** the entire table SHALL be wrapped in a `<fieldset>` with a visually hidden `<legend>` (the page title serves as label)
- **AND** each hype stop within a row SHALL be a `<label>` containing a visually hidden `<input type="radio">` and a visual dot `<span>`
- **AND** all radio inputs for one artist SHALL share a `name` attribute scoped to the artist (e.g., `hype-{artistId}`)
- **AND** the selected radio SHALL be `checked` via Aurelia's `model.bind`/`checked.bind` pattern

## REMOVED Requirements

### Requirement: Slider-level authentication gate

**Reason**: Authentication, onboarding, and signup-prompt logic are business concerns that belong in the parent route, not in a presentation component. The slider has no methods and dispatches no custom events. The parent listens for the native `change` event and applies all business logic.
**Migration**: Remove `selectHype()` method, `isAuthenticated` bindable, and `isOnboarding` bindable. Remove `INode` dependency (no custom event dispatch). Remove `click.trigger` from radio inputs. Change `hype` bindable to `twoWay` mode. Parent listens for native `change` event via `change.trigger` on the `<hype-inline-slider>` element.

## ADDED Requirements

### Requirement: Slider Track Vertical Centering

The slider track line SHALL be vertically centered within the slider grid cell using CSS logical properties.

#### Scenario: Track is vertically centered

- **WHEN** the slider renders
- **THEN** the `.hype-slider-track` element SHALL use `inset-block-start: 50%` and `translate: 0 -50%` to center vertically within the grid row
- **AND** the track SHALL remain centered across viewport sizes
