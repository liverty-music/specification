# PayoutSweeperUseCase.EnsureSettlementExists

## Purpose

PayoutSweeperUseCase.EnsureSettlementExists records the Held Settlement that pays out an issued Order's money to the event's Organizer.

## Requirements

### Requirement: Every issued order gets a Held settlement

When an Order is issued, EnsureSettlementExists SHALL record a Settlement for it with Settlement.Upsert: Held, for the event's Organizer and the event, with one split paying the Organizer its net share of the Order's amount. The platform fee kept from the Order's amount is TODO(threshold). When the Order already has a Settlement, the existing one SHALL be returned and nothing is added.

Known defect: liverty-music/backend#468

#### Scenario: Order issued

- **WHEN** an Order is issued for an event of an Organizer
- **THEN** a Held Settlement with one split for that Organizer exists for the Order

#### Scenario: Settlement already recorded

- **WHEN** EnsureSettlementExists runs for an Order that has a Settlement
- **THEN** the existing Settlement is returned and no second one is recorded
