# LotteryApplication.CreateAuthorization

## Purpose

Places a hold for the application's amount on the applicant's card; nothing is charged until a winning draw captures it.

## Requirements

### Requirement: Holding the application's amount

CreateAuthorization SHALL place a hold in Japanese yen for the given amount on the applicant's card and return a reference the applicant's client uses to confirm the card; no money moves until the hold is captured. It SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when card payments are not available.

#### Scenario: Hold placed

- **WHEN** CreateAuthorization is called with a positive amount
- **THEN** a hold for that amount in yen is placed and a reference to it is returned, and nothing is charged

#### Scenario: Non-positive amount

- **WHEN** CreateAuthorization is called with an amount of zero or less
- **THEN** it fails with InvalidArgument and no hold is placed

#### Scenario: Card payments unavailable

- **WHEN** card payments are not available
- **THEN** CreateAuthorization fails with Unavailable
