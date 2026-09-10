## Purpose

Establishes the Material 3 semantic token layer for the frontend — color roles with guaranteed `on-*`
pairings, state-layer opacities, spatial/effects motion, shape roles, and tonal surface tiers — expressed in
the project's oklch + CUBE CSS idiom so every component consumes M3 tokens instead of ad-hoc values.

## ADDED Requirements

### Requirement: Color roles with guaranteed on-color pairing

The token layer SHALL expose Material 3 color **roles** (`primary`, `secondary`, `tertiary`, their
`*-container` variants, `surface`, `surface-container-*` tiers, `outline`, `error`) where every fill role
has a paired `on-*` role. Components SHALL reference roles, not raw palette values, and any text/icon placed
on a fill SHALL use that fill's matching `on-*` role. Roles SHALL be expressed in oklch as aliases over the
existing brand/surface tokens; no hex or hsl literals are introduced.

#### Scenario: Fill and text use a matched role pair

- **WHEN** a component renders content on a `primary` (or `*-container`) fill
- **THEN** its text/icon color is the matching `on-primary` (or `on-*-container`) role, and the pair meets
  the contrast target (4.5:1 body text, 3:1 large text / UI boundaries)

#### Scenario: Dynamic-hue surfaces guarantee contrast

- **WHEN** a surface color is derived from a variable hue (e.g. an artist-hue card)
- **THEN** the on-color is chosen from the role system such that legibility holds across the full hue range,
  rather than assuming a fixed white/black overlay

#### Scenario: No raw palette leakage

- **WHEN** the stylesheet is audited for color usage
- **THEN** interactive component colors resolve through M3 role tokens (or their host aliases), and there are
  zero hard-coded hex/hsl color literals

### Requirement: State-layer opacity scale

The token layer SHALL define a single set of state-layer opacity tokens — hover 8%, focus 12%, pressed 12%,
dragged 16%, selected 12% — applied by overlaying the component's `on-*` role at that opacity. Interaction
feedback SHALL use these tokens rather than per-component one-off opacities or color swaps.

#### Scenario: Hover applies the shared 8% overlay

- **WHEN** a pointer hovers an interactive element
- **THEN** an 8% `on-*` state layer is composited over its base fill using the shared token, not a bespoke
  opacity value

#### Scenario: Keyboard focus uses focus-visible

- **WHEN** an element receives focus from the keyboard
- **THEN** the 12% focus state layer shows via `:focus-visible` (not bare `:focus`), so mouse clicks do not
  leave a stuck state layer

#### Scenario: Selected state persists and stacks

- **WHEN** an element is in a selected/activated state and is also hovered
- **THEN** the 12% selected layer persists and the hover layer stacks on top of it

### Requirement: Motion tokens split by property class

The token layer SHALL define motion tokens as standard and emphasized **easing** curves, a **duration**
scale, and **spring** approximations partitioned into **spatial** (with visible overshoot, for
transform/size/radius) and **effects** (no overshoot, for color/opacity). Components SHALL select a token by
the property being animated: spatial for movement/scale/shape, effects/standard for color/opacity.

#### Scenario: Positional change uses a spatial spring

- **WHEN** an element animates position, scale, or corner radius
- **THEN** it uses a spatial spring/emphasized token that may overshoot

#### Scenario: Opacity/color change uses a non-bouncy token

- **WHEN** an element animates color or opacity
- **THEN** it uses an effects/standard token with no overshoot

#### Scenario: Scattered raw timings are consolidated

- **WHEN** a transition or animation specifies timing
- **THEN** it references a motion duration/easing token rather than an inline raw millisecond value or an
  ad-hoc cubic-bezier

### Requirement: Shape roles including expressive steps

The token layer SHALL expose Material 3 shape **roles** (extra-small → full) as aliases over the existing
radius tokens, including the Expressive `-increased` emphasis steps, and SHALL use logical radius properties
so shapes mirror correctly in RTL. Radius SHALL match component size.

#### Scenario: Radius matches component size

- **WHEN** a component picks a corner radius
- **THEN** it selects the shape role appropriate to its size (small controls small radius, sheets extra-large,
  pills/avatars full), and an emphasis element may step up to an `-increased` role

#### Scenario: Directional rounding is RTL-safe

- **WHEN** only some corners are rounded (e.g. a bottom sheet's top edge)
- **THEN** logical radius properties are used so the rounding mirrors under RTL

### Requirement: Tonal surface-container tiers

The token layer SHALL provide at least five tonal surface tiers (`surface-container-lowest` through
`-highest`) so depth can be expressed by surface tier rather than shadow alone. Shadow SHALL be reserved for
genuinely floating overlays and, where used, SHALL be themeable (brand-tinted or via a shadow role), never a
hard-coded black shadow that disappears under `forced-colors`.

#### Scenario: Resting depth uses a tonal tier

- **WHEN** a resting (non-floating) surface needs to read as raised
- **THEN** it uses a higher surface-container tier rather than a cast shadow

#### Scenario: Surfaces survive forced-colors

- **WHEN** the UI renders under `forced-colors: active` / high-contrast
- **THEN** surfaces remain distinguishable via their tonal tier, not by shadow alone
