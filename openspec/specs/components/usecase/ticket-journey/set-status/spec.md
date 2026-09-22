# Set Status

## Purpose

Lets a user record and update their personal ticket-acquisition status for a concert, maintaining a single authoritative status per user per event as they progress from tracking through applying to paying.

## Requirements

### Requirement: Ticket-journey status is a single source of truth
Ticket-journey status SHALL be owned by a single observable store exposing an observable map of event id to journey status. Reads (`listByUser`) SHALL populate the store and SHALL be treated as always-fresh (network-first, no stale window). Writes (`SetStatus`, `Delete`) SHALL be write-through: they SHALL issue the RPC and then update the store's observable map. All consumers — the Dashboard and the event detail sheet — SHALL read journey status from this store, so a status change from any surface is reflected everywhere without a re-fetch or route re-entry. The store SHALL clear its journey state on sign-out.

#### Scenario: Sheet write reflects on the Dashboard without re-entry
- **WHEN** the user changes a journey status in the event detail sheet
- **THEN** the store's observable journey map SHALL be updated after the write RPC succeeds
- **AND** the Dashboard's rendering of that event's status SHALL update without re-fetching or re-entering the route

#### Scenario: Single shared journey state
- **WHEN** both the Dashboard and the detail sheet render a journey status for the same event
- **THEN** both SHALL read from the same observable map
- **AND** they SHALL NOT hold separate copies of the status

#### Scenario: Journey read is always fresh
- **WHEN** the Dashboard loads and requests journey status via the store
- **THEN** the store SHALL fetch `listByUser` fresh (no stale window)
- **AND** it SHALL surface the result via its observable map

#### Scenario: Write failure does not desync the store
- **WHEN** a journey `SetStatus`/`Delete` RPC fails
- **THEN** the store's observable map SHALL NOT be updated to the attempted value

#### Scenario: Journey state cleared on sign-out
- **WHEN** the user signs out
- **THEN** the store SHALL clear its journey map
- **AND** no prior user's journey status SHALL be readable afterward

### Requirement: Set Ticket Journey Status

The system SHALL allow an authenticated user to set (create or update) their ticket journey status for a given event via a single upsert operation. Status can be set manually by the user, as a side effect of confirming a ticket email import, **or as a first-party authoritative side effect of ⑤ `ticket-purchase-and-issuance` issuing a ticket** (which sets the status to `PAID` for that user and event, superseding any scraped/self-reported value).

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

#### Scenario: First-party issuance sets PAID

- **WHEN** ⑤ issues a ticket for a user's event
- **THEN** the system SHALL set that user's ticket-journey for the event to `PAID` as a first-party authoritative side effect (superseding any scraped/self-reported value)
