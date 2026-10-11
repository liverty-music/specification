# Spec Delta

## ADDED Requirements

### Requirement: A lottery window lasts 1 to 14 days

A TicketSale's end time SHALL be after its start time. When its method is Lottery, the window SHALL last at least 1 day and at most 14 days.

#### Scenario: Lottery window within bounds
- **WHEN** a Lottery sale runs for 10 days
- **THEN** the window is valid

#### Scenario: Lottery window shorter than 1 day
- **WHEN** a Lottery sale runs for 23 hours
- **THEN** the window is invalid

#### Scenario: Lottery window longer than 14 days
- **WHEN** a Lottery sale runs for 14 days and 1 hour
- **THEN** the window is invalid

#### Scenario: End not after start
- **WHEN** the end time equals or precedes the start time
- **THEN** the window is invalid

#### Scenario: First-come window longer than 14 days
- **WHEN** a FirstCome sale runs from 2026-11-01 10:00 to 2026-11-20 18:00
- **THEN** the window is valid

### Requirement: A sale has a name

A TicketSale's name SHALL be 1 to 100 characters.

#### Scenario: Named sale
- **WHEN** a sale is named ファンクラブ先行
- **THEN** the name is valid

#### Scenario: Empty name
- **WHEN** a sale has an empty name
- **THEN** the sale is invalid

### Requirement: Verification requirement

A sale SHALL require verification when its verification requirement is Verified-any or JPKI-only; both require the fan to hold an Active IdentityVerification. A sale created without a requirement SHALL have the requirement None.

#### Scenario: No requirement given
- **WHEN** a sale is created without a verification requirement
- **THEN** its requirement is None and it does not require verification

#### Scenario: Verified-any or JPKI-only
- **WHEN** the requirement is Verified-any or JPKI-only
- **THEN** the sale requires an Active IdentityVerification

### Requirement: Window open at an instant

A sale's window SHALL be open at an instant when the instant is at or after the start time and before the end time.

#### Scenario: Before start
- **WHEN** the instant precedes the start time
- **THEN** the window is not open

#### Scenario: Between start and end
- **WHEN** the instant is at the start time or later and before the end time
- **THEN** the window is open

#### Scenario: At end
- **WHEN** the instant is the end time or later
- **THEN** the window is not open

### Requirement: Two windows overlap

Two sales' windows SHALL overlap when each one starts before the other ends.

#### Scenario: Back to back
- **WHEN** one sale ends at 2026-11-10 23:59 and the other starts at 2026-11-10 23:59
- **THEN** the windows do not overlap

#### Scenario: Overlapping
- **WHEN** one sale runs from 1 to 10 November and the other from 8 to 20 November
- **THEN** the windows overlap

### Requirement: Drawn sale

A Lottery sale SHALL count as drawn once its draw time is set.

#### Scenario: Draw time set
- **WHEN** the draw time is set
- **THEN** the sale is drawn

#### Scenario: Draw time absent
- **WHEN** the draw time is absent
- **THEN** the sale is not drawn

## REMOVED Requirements

### Requirement: Sale window, price, quantity and limit
**Reason**: A TicketSale now holds only what is common to one sale opportunity across the events of a Series. The price, quantity and per-account limit are per event and move to the TicketType; the window rule is "A lottery window lasts 1 to 14 days" above, whose end-after-start rule holds for both methods.
**Migration**: entity/ticket-type "Price, quantity and per-account limit" carries the price, quantity and limit rules, the default limit of 4 included. Each shipped first-come sale becomes one sale with one TicketType in this change's migration.

### Requirement: Remaining tickets
**Reason**: The stock is counted per event, so the remaining count is a TicketType's.
**Migration**: entity/ticket-type "Remaining tickets", counting the TicketType's holding Checkouts.

### Requirement: Sale state at a time
**Reason**: The state is read per TicketType, because SoldOut, AllHeld and LowStock count one event's stock; NotYetOnSale and Ended still come from the sale's window.
**Migration**: entity/ticket-type "Sale state at a time".

### Requirement: Price fixed while tickets are held or sold
**Reason**: The price is a TicketType's.
**Migration**: entity/ticket-type "Price fixed while tickets are held or sold".
