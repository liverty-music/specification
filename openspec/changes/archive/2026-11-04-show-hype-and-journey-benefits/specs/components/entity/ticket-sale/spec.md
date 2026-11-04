## ADDED Requirements

### Requirement: Only a discovered lottery has a result date

A TicketSale's result date SHALL be the calendar day, in Japan time (Asia/Tokyo), on which the lottery's results are announced. Only a discovered Lottery sale MAY have one, and it SHALL be no earlier than the calendar day of the sale's end time in Japan time. A sale without a result date is valid.

#### Scenario: Discovered lottery with a result date

- **WHEN** a discovered lottery closes on 22 October 23:59 and its result date is 3 November
- **THEN** the sale is valid

#### Scenario: Result date before the close

- **WHEN** a discovered lottery closes on 22 October 23:59 and its result date is 20 October
- **THEN** the sale is invalid

#### Scenario: First-come sale with a result date

- **WHEN** a discovered first-come sale has a result date
- **THEN** the sale is invalid

#### Scenario: Organizer's lottery with a result date

- **WHEN** an Organizer's lottery has a result date
- **THEN** the sale is invalid

#### Scenario: Discovered lottery without a result date

- **WHEN** a discovered lottery has no result date
- **THEN** the sale is valid
