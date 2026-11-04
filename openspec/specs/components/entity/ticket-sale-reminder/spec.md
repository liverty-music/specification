# components/entity/ticket-sale-reminder Specification

## Purpose
A Ticket Sale Reminder records that one reminder stage of one TicketSale has been sent to one User, so the same reminder is not sent to that user again. It links a User and a TicketSale, discovered or an Organizer's, and carries the stage and the time it was sent.

| attribute | meaning | constraint |
|---|---|---|
| user | The fan the reminder was sent to | required |
| ticket sale | The TicketSale the reminder is about | required |
| stage | Which point of the sale's timeline the reminder marks: `APPLY_OPEN`, `APPLY_CLOSE_24H`, `RESULT_DAY` | required; only defined values |
| sent time | When the reminder was recorded as sent | required, set when the record is created |

```mermaid
erDiagram
    User ||--o{ TicketSaleReminder : "was reminded"
    TicketSale ||--o{ TicketSaleReminder : "is reminded by"
```

## Requirements

### Requirement: Stage values are closed

A ticket sale reminder's stage SHALL be one of `APPLY_OPEN`, `APPLY_CLOSE_24H` or `RESULT_DAY`; any other value SHALL be invalid.

#### Scenario: Undefined stage
- **WHEN** a reminder carries a stage that is not one of the three defined stages
- **THEN** the reminder is invalid

#### Scenario: Result day stage
- **WHEN** a reminder carries the stage `RESULT_DAY`
- **THEN** the reminder is valid

### Requirement: Stages by method

A reminder stage SHALL be anchored on exactly one milestone of the TicketSale, and only these stages SHALL apply, alike to a discovered sale and to an Organizer's sale unless stated:

- `APPLY_OPEN`: on a Lottery sale, at the start time. On a FirstCome sale, 30 minutes before the start time.
- `APPLY_CLOSE_24H`: on a Lottery sale only, 24 hours before the end time.
- `RESULT_DAY`: on a discovered Lottery sale with a result date only, at 09:00 on the result date in the fan's time zone.

#### Scenario: Lottery stages
- **WHEN** a Lottery sale opens on 5 October 18:00 and closes on 22 October 23:59
- **THEN** `APPLY_OPEN` is anchored on 5 October 18:00 and `APPLY_CLOSE_24H` on 21 October 23:59

#### Scenario: First-come stage
- **WHEN** a FirstCome sale opens on 6 October 19:00
- **THEN** `APPLY_OPEN` is anchored on 6 October 18:30, and `APPLY_CLOSE_24H` does not apply

#### Scenario: Result day stage
- **WHEN** a discovered Lottery sale has the result date 3 November and the fan's time zone is Asia/Tokyo
- **THEN** `RESULT_DAY` is anchored on 3 November 09:00 Asia/Tokyo

#### Scenario: Lottery without a result date
- **WHEN** a discovered Lottery sale has no result date, or the sale is an Organizer's lottery
- **THEN** `RESULT_DAY` does not apply
