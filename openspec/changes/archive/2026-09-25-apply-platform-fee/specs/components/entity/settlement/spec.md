## ADDED Requirements

### Requirement: Platform fee rate

The platform fee SHALL be a flat 5% of the Order's amount, rounded down to the nearest whole yen (`floor(amount × 5 ÷ 100)`, computed with integer arithmetic). The Organizer's split SHALL be the Order's amount minus this fee, so the Organizer's split absorbs the rounding remainder, not the platform.

#### Scenario: Round order amount

- **WHEN** the Order's amount is 10000 yen
- **THEN** the platform fee is 500 yen and the Organizer's split is 9500 yen

#### Scenario: Amount that does not divide evenly

- **WHEN** the Order's amount is 3333 yen
- **THEN** the platform fee is 166 yen and the Organizer's split is 3167 yen

#### Scenario: Fee rounds down to zero

- **WHEN** the Order's amount is 19 yen or less
- **THEN** the platform fee is 0 yen and the Organizer's split is the full amount

## MODIFIED Requirements

### Requirement: Splits and platform fee

A Settlement SHALL have at least one split, every split amount SHALL be greater than 0, and the sum of the split amounts SHALL NOT exceed its Order's amount. The platform fee is the Order's amount minus the sum of the split amounts. The venue is the Organizer's own cost and is never a payee.

#### Scenario: Single Organizer split

- **WHEN** the Order's amount is 16000 yen and the only split pays the Organizer 15200 yen
- **THEN** the splits are valid and the platform fee is 800 yen

#### Scenario: No split

- **WHEN** a Settlement has no split
- **THEN** its splits are invalid

#### Scenario: Non-positive split

- **WHEN** a split amount is 0 or less
- **THEN** its splits are invalid

#### Scenario: Splits exceed the order

- **WHEN** the split amounts add up to more than the Order's amount
- **THEN** its splits are invalid
