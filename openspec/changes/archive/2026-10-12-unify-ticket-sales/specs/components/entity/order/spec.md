# Spec Delta

## MODIFIED Requirements

### Requirement: An Order has exactly one source

An Order SHALL come from exactly one source: a Won LotteryEntry, or a Checkout that was Committed and charged and is Completed by the Order's issuance. An Order that names both, or neither, SHALL be invalid. At most one Order SHALL exist per source.

#### Scenario: Order from a checkout

- **WHEN** an Order names a Checkout and no LotteryEntry
- **THEN** its source is valid

#### Scenario: Order from a won lottery entry

- **WHEN** an Order names a LotteryEntry and no Checkout
- **THEN** its source is valid

#### Scenario: Two sources

- **WHEN** an Order names both a LotteryEntry and a Checkout
- **THEN** the Order is invalid
