# components/infrastructure/organizer/web/route/ticket-sale-editor Specification

## Purpose
The organizer console screen where an operator puts one published event on sale first come, first served, or changes that sale, and sees how many tickets have sold.

## Requirements

### Requirement: Sale settings with sensible defaults

For an event without a sale, the screen SHALL offer the sale start and sale end, entered in Japan time, the price per ticket 税込 (tax-inclusive), the quantity and the per-account limit, with the sale end defaulting to the event's start time and the limit defaulting to 4. It SHALL show an error next to a field, without saving, when the sale end is after the event's start time, the end is not after the start, the price is outside 1 to 1,000,000 yen, the quantity is below 1, or the limit is outside 1 to 10.

#### Scenario: Blank form

- **WHEN** an operator opens the editor for an event starting 2026-11-20 19:00
- **THEN** the sale end is 2026-11-20 19:00 and the limit is 4

#### Scenario: End after the show starts

- **WHEN** the operator sets the sale end to 19:30 for a 19:00 show and saves
- **THEN** an error is shown next to the sale end and nothing is saved

### Requirement: What can change once the sale has started

For an event with a sale, the screen SHALL show the quantity, the sold count and the held count. While any ticket is sold or held, it SHALL show the price as fixed, and it SHALL refuse a quantity below what is sold and held, saying why.

#### Scenario: Price locked

- **WHEN** the operator opens the editor while a fan's checkout holds 2 tickets
- **THEN** the price cannot be edited and the screen says it is fixed while tickets are held or sold

### Requirement: Prerequisites explained

When the event is not published, has no start time, or the Organizer has no complete seller details, the screen SHALL say which is missing and not offer to save. For missing seller details, it SHALL say they are entered by Liverty Music during vetting.

#### Scenario: No start time

- **WHEN** the operator opens the editor for an event without a start time
- **THEN** the screen says to set the start time in the concert editor first and links to it
