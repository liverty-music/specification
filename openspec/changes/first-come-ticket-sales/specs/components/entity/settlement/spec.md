# Spec Delta

## MODIFIED Requirements

### Requirement: Platform fee rate

The platform fee SHALL be the Order's amount times the Organizer's platform fee rate at the time the Settlement is created, rounded down to the nearest whole yen (`floor(amount × rate ÷ 10000)` with the rate in hundredths of a percent, computed with integer arithmetic). The rate SHALL be kept on the Settlement, so a later change to the Organizer's rate never changes it. The Organizer's split SHALL be the Order's amount minus this fee, so rounding favours the Organizer.

#### Scenario: Round order amount

- **WHEN** the Order's amount is 10000 yen and the Organizer's rate is 8%
- **THEN** the platform fee is 800 yen and the Organizer's split is 9200 yen

#### Scenario: Pilot rate

- **WHEN** the Order's amount is 10000 yen and the Organizer's rate is 5%
- **THEN** the platform fee is 500 yen and the Organizer's split is 9500 yen

#### Scenario: Amount that does not divide evenly

- **WHEN** the Order's amount is 3333 yen and the rate is 8%
- **THEN** the platform fee is 266 yen and the Organizer's split is 3067 yen

#### Scenario: Fee rounds down to zero

- **WHEN** the Order's amount is 12 yen and the rate is 8%
- **THEN** the platform fee is 0 yen and the Organizer's split is the full amount

#### Scenario: Rate changed after issuance

- **WHEN** the Organizer's rate changes from 5% to 8% after a Settlement was created at 5%
- **THEN** that Settlement keeps its 5% fee
