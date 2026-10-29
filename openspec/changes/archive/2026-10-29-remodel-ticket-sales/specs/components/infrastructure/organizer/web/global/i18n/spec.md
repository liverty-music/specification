# Spec Delta

## MODIFIED Requirements

### Requirement: Prices in yen with separators

Every price the console shows SHALL be in yen with digit separators and no decimal places, formatted for the current language (for example `6,500円` in Japanese and `¥6,500` in English). Counts of tickets and entries SHALL also show digit separators.

#### Scenario: Ticket price

- **WHEN** a SeatType's price is 6500 yen and the console is in Japanese
- **THEN** the price is shown as 6,500円

#### Scenario: Large count

- **WHEN** a sale has 1380 requested tickets
- **THEN** the count is shown as 1,380
