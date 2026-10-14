# Spec Delta

## MODIFIED Requirements

### Requirement: State-layer opacity scale

The token layer SHALL define a single set of state-layer opacity tokens — hover 8%, focus 10%, pressed 10%, dragged 16%, selected 12% — applied by overlaying the component's `on-*` role at that opacity. Interaction
feedback SHALL use these tokens rather than per-component one-off opacities or color swaps.

#### Scenario: Hover applies the shared 8% overlay

- **WHEN** a pointer hovers an interactive element
- **THEN** an 8% `on-*` state layer is composited over its base fill using the shared token, not a bespoke
  opacity value

#### Scenario: Keyboard focus uses focus-visible

- **WHEN** an element receives focus from the keyboard
- **THEN** the 10% focus state layer shows via `:focus-visible` (not bare `:focus`), so mouse clicks do not
  leave a stuck state layer

#### Scenario: Selected state persists and stacks

- **WHEN** an element is in a selected/activated state and is also hovered
- **THEN** the 12% selected layer persists and the hover layer stacks on top of it

#### Scenario: Press applies the shared 10% overlay

- **WHEN** a pointer presses an interactive element
- **THEN** a 10% `on-*` state layer is composited over its base fill

## ADDED Requirements

### Requirement: Easing curves and durations match Material 3

The motion tokens SHALL use the Material 3 values: easing standard `cubic-bezier(0.2, 0, 0, 1)`, standard-decelerate `cubic-bezier(0, 0, 0, 1)`, standard-accelerate `cubic-bezier(0.3, 0, 1, 1)`, emphasized-decelerate `cubic-bezier(0.05, 0.7, 0.1, 1)` and emphasized-accelerate `cubic-bezier(0.3, 0, 0.8, 0.15)`; durations short 50/100/150/200 ms, medium 250/300/350/400 ms, long 450/500/550/600 ms and extra-long 700/800/900/1000 ms.

#### Scenario: Leaving element accelerates

- **WHEN** an element leaves the screen with the emphasized-accelerate token
- **THEN** its timing curve is `cubic-bezier(0.3, 0, 0.8, 0.15)`: slow at first and fastest at the end

### Requirement: State and motion tokens are shared with the organizer console

The state-layer opacities, easing curves and durations SHALL be defined once and used by both the fan app and the organizer console, so a change to one of them applies to both. Color, type and shape values are not shared: each app keeps its own values under the same role names.

#### Scenario: One edit applies to both apps

- **WHEN** the hover opacity is changed in the shared definition
- **THEN** the fan app and the organizer console both use the new value, with no other edit

#### Scenario: Colors stay per app

- **WHEN** the organizer console renders its light `surface`
- **THEN** the fan app's dark navy `surface` is unchanged
