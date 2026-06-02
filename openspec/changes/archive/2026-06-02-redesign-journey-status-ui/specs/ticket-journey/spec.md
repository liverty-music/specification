## ADDED Requirements

### Requirement: Ticket Status UI two-phase layout

The Ticket Status control in `EventDetailSheet` SHALL present the journey statuses in two phases instead of a flat row: a **process phase** (`TRACKING ▸ APPLIED`) and an **outcome phase**. The outcome phase SHALL stack its routes vertically with the success route (`UNPAID → PAID`, grouped under a "当選" heading) above the failure route (`LOST`).

#### Scenario: Process phase shows the pre-result sequence

- **WHEN** an authenticated user opens the concert detail sheet
- **THEN** the process phase SHALL render `TRACKING` and `APPLIED` as a horizontal segmented sequence in that order

#### Scenario: Outcome phase stacks success above failure

- **WHEN** the outcome phase is rendered
- **THEN** the success route (`UNPAID` then `PAID`) SHALL appear above the failure route (`LOST`)
- **AND** `UNPAID` and `PAID` SHALL be grouped under a single "当選" heading

### Requirement: Ticket Status cumulative progress display

The Ticket Status control SHALL derive and display the user's progress through the journey from the single stored status, using the fixed journey DAG (`TRACKING → APPLIED → {LOST | UNPAID → PAID}`). States already passed SHALL be shown as completed, the current state SHALL be the only solid-filled node, and not-yet-reached states SHALL be shown as outlined.

#### Scenario: Passed states are marked completed

- **WHEN** the current status is `PAID`
- **THEN** `TRACKING`, `APPLIED`, and `UNPAID` SHALL be displayed as completed (e.g. a check cue)
- **AND** `PAID` SHALL be displayed as the current solid-filled node

#### Scenario: Future states are outlined

- **WHEN** the current status is `APPLIED`
- **THEN** `APPLIED` SHALL be the solid-filled node
- **AND** `TRACKING` SHALL be displayed as completed
- **AND** the outcome states SHALL be displayed as not-yet-reached (outlined)

#### Scenario: Exactly one solid-filled node

- **WHEN** any status is selected
- **THEN** exactly one node SHALL be solid-filled at a time

### Requirement: Ticket Status selection contrast

The currently selected status SHALL be conveyed primarily through a solid fill versus outlined unselected states, rather than through background color intensity or opacity. The selected node SHALL remain clearly distinguishable from unselected nodes for every status value, including `LOST`.

#### Scenario: Selected LOST is clearly distinguishable

- **WHEN** the current status is `LOST`
- **THEN** the `LOST` node SHALL be solid-filled
- **AND** it SHALL be visually distinct from the unselected/outlined nodes

### Requirement: Ticket Status semantic color and non-color cues

Each status SHALL carry a meaning-based color and a non-color cue (icon plus text label) so the control is understandable without relying on color alone. `UNPAID` SHALL be the highest-attention color (amber/orange) to signal a required payment action, `PAID` SHALL use a success color (green), `LOST` SHALL use a failure color (red), and `TRACKING`/`APPLIED` SHALL use neutral/in-progress colors.

#### Scenario: UNPAID is emphasized as action-required

- **WHEN** the current status is `UNPAID`
- **THEN** the `UNPAID` node SHALL use the highest-attention (amber/orange) color
- **AND** it SHALL include a non-color action cue

#### Scenario: Meaning survives without color

- **WHEN** any status node is rendered
- **THEN** it SHALL include a text label and a non-color cue (icon) in addition to color

### Requirement: Ticket Status outcome gating

The outcome phase SHALL be visually de-emphasized (dimmed, with a "結果待ち" affordance) until the `APPLIED` state has been reached, while remaining selectable at all times. Selecting the failure route SHALL de-emphasize the success route and vice-versa.

#### Scenario: Outcome dimmed before applied

- **WHEN** the current status is `TRACKING` or `APPLIED`
- **THEN** the outcome phase SHALL be displayed dimmed with a "結果待ち" affordance
- **AND** the outcome states SHALL still be selectable

#### Scenario: Mutually exclusive routes

- **WHEN** the current status is `LOST`
- **THEN** the success route (`UNPAID`/`PAID`) SHALL be dimmed
- **AND WHEN** the current status is `UNPAID` or `PAID`
- **THEN** the failure route (`LOST`) SHALL be dimmed

#### Scenario: Any status remains settable

- **WHEN** the user taps any status node, including a dimmed one
- **THEN** the control SHALL set that status via `TicketJourneyService/SetStatus`
- **AND** the UI SHALL NOT block the selection (no enforced state machine)

### Requirement: Ticket Status radiogroup accessibility

The Ticket Status control SHALL expose single-select semantics as a `role="radiogroup"` containing `role="radio"` options with `aria-checked` reflecting the current status. Each option SHALL be an accessible, ≥44px tap target.

#### Scenario: Radiogroup semantics

- **WHEN** the Ticket Status control is rendered for an authenticated user
- **THEN** it SHALL be a `radiogroup` of `radio` options
- **AND** the option matching the current status SHALL have `aria-checked="true"`
- **AND** all other options SHALL have `aria-checked="false"`
