## ADDED Requirements

### Requirement: Global button press feedback baseline
Every native `<button>` SHALL give an immediate, touch-visible press response on `:active` from an app-wide baseline, so no per-component code is needed for plain buttons. The baseline SHALL live in `@layer global` so component `:active` rules in `@layer block` keep precedence.

#### Scenario: Plain button responds on press
- **WHEN** a user presses a native `<button>` that defines no `:active` rule of its own
- **THEN** the button SHALL render a brief scale-down press cue (`transform: scale(<0.98..0.97>)`)
- **AND** the press-in SHALL use a fast (~50ms) `ease-in` transition consistent with the existing component convention

#### Scenario: Disabled button gives no feedback
- **WHEN** a user presses a `<button disabled>`
- **THEN** no press cue SHALL be applied (the baseline targets `:active:not(:disabled)`)

#### Scenario: Component-defined press feedback wins
- **WHEN** a component already defines its own `:active` rule in `@layer block`
- **THEN** the component rule SHALL take precedence over the global baseline
- **AND** the component's existing press behavior SHALL be unchanged

### Requirement: Non-button primary tappables give press feedback
Primary tappables that are rendered as `<a>` elements — which the `<button>` baseline cannot reach — SHALL define their own `:active` press feedback. Plain text navigation links are exempt.

#### Scenario: Bottom navigation tab responds on press
- **WHEN** a user taps a bottom-nav tab (`<a class="nav-tab">`)
- **THEN** the tab SHALL render a press cue at the moment of tap, distinct from the persistent selected-tab state

#### Scenario: Dashboard discover CTA responds on press
- **WHEN** a user taps the guest/empty-state primary CTA (`.discover-cta`), an `<a>` styled as a button
- **THEN** the CTA SHALL render a press cue consistent with the button baseline

#### Scenario: Plain text links are exempt
- **WHEN** an `<a>` is a plain text navigation link (e.g., a "back to dashboard" link, the not-found link)
- **THEN** no press scale cue is required, as a press scale is not expected for text links

### Requirement: List rows give press feedback
Full-width list rows SHALL acknowledge a tap with a background-deepen rather than a scale, so the cue reads correctly across the full row width regardless of whether the row is a `<button>` or an `<a>`.

#### Scenario: Settings row responds on press
- **WHEN** a user taps a settings list row (`.settings-row`)
- **THEN** the row SHALL deepen its background on `:active`
- **AND** the global button scale SHALL be suppressed (`transform: none`) so button-rows and anchor-rows feel identical

### Requirement: Reduced motion fallback for press feedback
Under `prefers-reduced-motion: reduce`, every press cue SHALL drop the motion (scale) but keep a non-motion acknowledgement so the tap still registers.

#### Scenario: Button press under reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active and a user presses a button
- **THEN** the scale cue SHALL be suppressed
- **AND** a non-motion cue (e.g., reduced opacity) SHALL acknowledge the press

#### Scenario: Nav tab press under reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active and a user taps a nav tab
- **THEN** the scale cue SHALL be suppressed
- **AND** a non-motion cue (e.g., a brief accent-tinted background) SHALL acknowledge the tap

### Requirement: Touch activation reliability on iOS Safari
Press feedback SHALL be applied only via `:active` on elements that satisfy iOS Safari's `:active` activation rule (the element or an ancestor has `cursor: pointer`, or the element is an `<a href>`).

#### Scenario: Button satisfies the iOS activation rule
- **WHEN** the targeted element is a native `<button>`
- **THEN** it SHALL inherit `cursor: pointer` from the reset, so iOS Safari applies `:active` on tap

#### Scenario: Anchor tappables satisfy the iOS activation rule
- **WHEN** the targeted element is an `<a>` tappable (nav tab, discover CTA)
- **THEN** it SHALL carry an `href`, so iOS Safari applies `:active` on tap
