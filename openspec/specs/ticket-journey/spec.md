# ticket-journey Specification

## Purpose

The `ticket-journey` capability allows users to track their personal ticket acquisition status for concerts and events. Users can set, update, and remove journey statuses representing stages of the ticket acquisition process (tracking, applied, lost, unpaid, paid).
## Requirements
### Requirement: Ticket Journey Entity

The system SHALL define a `TicketJourney` entity representing a user's personal ticket acquisition status for a specific event. Each journey is uniquely identified by the combination of user and event.

#### Scenario: TicketJourney data model

- **WHEN** a ticket journey is represented
- **THEN** it SHALL include a `user_id` (UserId), `event_id` (EventId), and `status` (TicketJourneyStatus)
- **AND** the composite key SHALL be `(user_id, event_id)` — one journey per user per event

#### Scenario: TicketJourneyStatus enum values

- **WHEN** a ticket journey status is represented
- **THEN** it SHALL be one of: `TRACKING`, `APPLIED`, `LOST`, `UNPAID`, `PAID`
- **AND** `UNSPECIFIED` (value 0) SHALL exist as the default proto value but SHALL NOT be accepted in API requests
- **AND** `LOST` SHALL represent both lottery failure and payment deadline expiration

### Requirement: Set Ticket Journey Status

The system SHALL allow an authenticated user to set (create or update) their ticket journey status for a given event via a single upsert operation. Status can be set manually by the user or as a side effect of confirming a ticket email import.

#### Scenario: Set status on a new journey

- **WHEN** an authenticated user calls `SetStatus` with an `event_id` and `status`
- **AND** no journey exists for that user and event
- **THEN** the system SHALL create a new `TicketJourney` with the given status
- **AND** the user_id SHALL be derived from the authentication context

#### Scenario: Update status on an existing journey

- **WHEN** an authenticated user calls `SetStatus` with an `event_id` and `status`
- **AND** a journey already exists for that user and event
- **THEN** the system SHALL update the existing journey's status

#### Scenario: Any status transition is allowed

- **WHEN** a user calls `SetStatus` with any valid status value
- **THEN** the system SHALL accept the transition regardless of the current status
- **AND** the system SHALL NOT enforce a state machine or transition rules

#### Scenario: Invalid status value rejected

- **WHEN** a user calls `SetStatus` with `UNSPECIFIED` or an undefined enum value
- **THEN** the system SHALL return an `INVALID_ARGUMENT` error

#### Scenario: Invalid event_id rejected

- **WHEN** a user calls `SetStatus` with a malformed or missing `event_id`
- **THEN** the system SHALL return an `INVALID_ARGUMENT` error

#### Scenario: Status set via ticket email confirmation

- **WHEN** a user confirms a ticket email import via `UpdateTicketEmail`
- **THEN** the system SHALL set the `TicketJourney` status for each associated event based on the parsed email content
- **AND** for `LOTTERY_INFO` emails, the status SHALL be set to `TRACKING`
- **AND** for `LOTTERY_RESULT` emails with a win and pending payment, the status SHALL be set to `UNPAID`
- **AND** for `LOTTERY_RESULT` emails with a win and completed payment, the status SHALL be set to `PAID`
- **AND** for `LOTTERY_RESULT` emails with a loss, the status SHALL be set to `LOST`

### Requirement: Delete Ticket Journey

The system SHALL allow an authenticated user to remove their ticket journey for a given event.

#### Scenario: Delete an existing journey

- **WHEN** an authenticated user calls `Delete` with an `event_id`
- **AND** a journey exists for that user and event
- **THEN** the system SHALL remove the journey record

#### Scenario: Delete a non-existent journey

- **WHEN** an authenticated user calls `Delete` with an `event_id`
- **AND** no journey exists for that user and event
- **THEN** the system SHALL return successfully (idempotent delete)

### Requirement: List Ticket Journeys by User

The system SHALL allow an authenticated user to retrieve all their ticket journeys.

#### Scenario: User has journeys

- **WHEN** an authenticated user calls `ListByUser`
- **THEN** the system SHALL return all `TicketJourney` records for that user
- **AND** each record SHALL contain `event_id` and `status`

#### Scenario: User has no journeys

- **WHEN** an authenticated user calls `ListByUser`
- **AND** the user has no ticket journeys
- **THEN** the system SHALL return an empty list

### Requirement: Ticket Journey Database Schema

The system SHALL store ticket journeys in a `ticket_journeys` table with a composite primary key.

#### Scenario: Table structure

- **WHEN** the `ticket_journeys` table is created
- **THEN** it SHALL have columns: `user_id` (UUID, FK -> users), `event_id` (UUID, FK -> events), `status` (SMALLINT)
- **AND** the primary key SHALL be `(user_id, event_id)`
- **AND** it SHALL NOT include `created_at` or `updated_at` columns

#### Scenario: Upsert operation

- **WHEN** a `SetStatus` operation targets an existing `(user_id, event_id)` pair
- **THEN** the database SHALL perform `INSERT ... ON CONFLICT (user_id, event_id) DO UPDATE SET status`

### Requirement: Ticket Status UI visibility

The Ticket Status UI in `EventDetailSheet` SHALL only be rendered when the user is authenticated. Unauthenticated (guest) users SHALL NOT see the Ticket Status section.

#### Scenario: Authenticated user sees Ticket Status section

- **WHEN** an authenticated user opens the concert detail sheet
- **THEN** the Ticket Status section SHALL be visible
- **AND** the user SHALL be able to select a status (TRACKING, APPLIED, LOST, UNPAID, PAID)

#### Scenario: Unauthenticated user does not see Ticket Status section

- **WHEN** an unauthenticated (guest) user opens the concert detail sheet
- **THEN** the Ticket Status section SHALL NOT be rendered
- **AND** no RPC call to `TicketJourneyService/SetStatus` SHALL be made

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

