# Spec Delta

## ADDED Requirements

### Requirement: An Organizer's sale names events, a discovered sale none

A TicketSale of a Series that has an Organizer SHALL be that Organizer's sale. It SHALL name at least one event, each an event of its Series, SHALL sell every TicketStock of the events it names, and SHALL have no discovered time. A TicketSale of a Series without an Organizer SHALL be a discovered sale. It SHALL name no event, SHALL have a discovered time and SHALL have the verification requirement None.

#### Scenario: Organizer's presale
- **WHEN** a sale belongs to a Series owned by an Organizer and names two of its events
- **THEN** it is the Organizer's sale and sells every TicketStock of those two events

#### Scenario: Sale found by discovery
- **WHEN** a sale belongs to a Series that has no Organizer
- **THEN** it is a discovered sale and names no event

#### Scenario: Discovered sale naming an event
- **WHEN** a sale of a Series without an Organizer names an event
- **THEN** the sale is invalid

#### Scenario: Organizer's sale without an event
- **WHEN** a sale of a Series with an Organizer names no event
- **THEN** the sale is invalid

#### Scenario: Event of another Series
- **WHEN** an Organizer's sale names an event of another Series
- **THEN** the sale is invalid

### Requirement: Every sale has a name

Every TicketSale, an Organizer's or a discovered one, SHALL have a name of 1 to 100 characters, the label fans see, such as ファンクラブ先行.

#### Scenario: Named sale
- **WHEN** a sale is named ファンクラブ先行
- **THEN** the name is valid

#### Scenario: Empty name
- **WHEN** a sale has an empty name
- **THEN** the sale is invalid

#### Scenario: Discovered sale with a name
- **WHEN** a discovered sale is named オフィシャル先行
- **THEN** the sale is valid

### Requirement: Every sale has a start and an end time

Every TicketSale SHALL have a start time and an end time.

#### Scenario: Both times
- **WHEN** a sale has a start time and an end time
- **THEN** the sale is valid

#### Scenario: Lottery without a close
- **WHEN** a Lottery sale has no end time
- **THEN** the sale is invalid

#### Scenario: First-come sale without a close
- **WHEN** a FirstCome sale, an Organizer's or a discovered one, has no end time
- **THEN** the sale is invalid

### Requirement: Drawn lottery

An Organizer's Lottery sale SHALL count as drawn at an instant, given its LotteryEntries, when the instant is at or after its end time and none of its entries is Entered. A closed sale with no entries SHALL count as drawn.

#### Scenario: Closed with entries still Entered
- **WHEN** a Lottery sale has closed and one of its entries is Entered
- **THEN** the sale is not drawn

#### Scenario: Every entry decided
- **WHEN** a Lottery sale has closed and every one of its entries is Won or Lost
- **THEN** the sale is drawn

#### Scenario: Closed without entries
- **WHEN** a Lottery sale has closed and has no entries
- **THEN** the sale is drawn

#### Scenario: Still open
- **WHEN** a Lottery sale's end time is after the instant
- **THEN** the sale is not drawn

### Requirement: A sale is not yet over before its end time

A TicketSale SHALL be not yet over at an instant that is before its end time.

#### Scenario: Lottery before its close
- **WHEN** a Lottery sale closes on 22 October 23:59 and the instant is 20 October
- **THEN** the sale is not yet over

#### Scenario: First-come sale after its close
- **WHEN** a FirstCome sale closes at 20:00 and the instant is 20:00
- **THEN** the sale is over

## MODIFIED Requirements

### Requirement: A lottery window lasts 1 to 14 days

A TicketSale's end time SHALL be after its start time. When an Organizer's sale has the method Lottery, its window SHALL last at least 1 day and at most 14 days. A discovered sale's window SHALL have no limit on its length.

#### Scenario: Lottery window within bounds
- **WHEN** an Organizer's Lottery sale runs for 10 days
- **THEN** the window is valid

#### Scenario: Lottery window shorter than 1 day
- **WHEN** an Organizer's Lottery sale runs for 23 hours
- **THEN** the window is invalid

#### Scenario: Lottery window longer than 14 days
- **WHEN** an Organizer's Lottery sale runs for 14 days and 1 hour
- **THEN** the window is invalid

#### Scenario: End not after start
- **WHEN** the end time equals or precedes the start time
- **THEN** the window is invalid

#### Scenario: Discovered lottery longer than 14 days
- **WHEN** a discovered Lottery sale runs from 1 October to 31 October
- **THEN** the window is valid

#### Scenario: First-come window longer than 14 days
- **WHEN** a FirstCome sale runs from 2026-11-01 10:00 to 2026-11-20 18:00
- **THEN** the window is valid

## REMOVED Requirements

### Requirement: An Organizer's sale or a discovered sale

**Reason**: An Organizer's sale now names events and sells their TicketStocks instead of offering TicketTypes.
**Migration**: See "An Organizer's sale names events, a discovered sale none".

### Requirement: A sale has a name

**Reason**: Every sale, discovered ones too, now has a name; discovery reads it from the sale's page.
**Migration**: See "Every sale has a name". Discovered sales are re-read by discovery; the data deletion of this change does not touch them, and a discovered sale without a name is filled on its next discovery or skipped (components/entity/ticket-sale/upsert-discovered).

### Requirement: Required times depend on the method and the kind of sale

**Reason**: The lottery result time and the first-come sale "until sold out" are removed; every sale has an end time.
**Migration**: See "Every sale has a start and an end time". Discovery skips a sale whose end time it cannot find.

### Requirement: Result time of a lottery

**Reason**: The lottery result time is removed. Its only reader was the `RESULT_DAY` reminder, which is removed too; a fan of an Organizer's lottery is told the result directly.
**Migration**: None; the `lottery_result_at` column is dropped by this change's migration.

### Requirement: Drawn sale

**Reason**: The draw time is removed; whether a lottery is drawn follows from its entries.
**Migration**: See "Drawn lottery".

### Requirement: A sale not yet over

**Reason**: A sale without an end time no longer exists.
**Migration**: See "A sale is not yet over before its end time".
