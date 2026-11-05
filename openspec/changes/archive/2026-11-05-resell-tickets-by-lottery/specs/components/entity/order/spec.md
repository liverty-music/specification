# Spec Delta

## MODIFIED Requirements

### Requirement: An Order has exactly one source

An Order SHALL be applied for through exactly one source: one LotteryEntry, one Checkout or one ResaleEntry that names it. An Order that two sources name, or that none names, SHALL be invalid.

#### Scenario: Order from a checkout

- **WHEN** a Checkout names an Order and no LotteryEntry or ResaleEntry does
- **THEN** its source is valid

#### Scenario: Order from a won lottery entry

- **WHEN** a LotteryEntry names an Order and no Checkout or ResaleEntry does
- **THEN** its source is valid

#### Scenario: Order from a resale entry

- **WHEN** a ResaleEntry names an Order and no LotteryEntry or Checkout does
- **THEN** its source is valid

#### Scenario: Two sources

- **WHEN** a LotteryEntry and a ResaleEntry name the same Order
- **THEN** the Order is invalid
