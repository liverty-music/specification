# Spec Delta

## ADDED Requirements

### Requirement: A sale is returned only with its name, method, start and end from the pages

Every value in a discovered sale SHALL come from the searched pages; a value SHALL never be guessed. A sale SHALL be returned only when the pages state its name, its method, its start time and its end time. Otherwise the sale SHALL be discarded.

#### Scenario: Lottery with its application period
- **WHEN** a lottery's page names it オフィシャル先行 and states its application period
- **THEN** the discovered sale has the name オフィシャル先行, method Lottery, a start time and an end time

#### Scenario: First-come sale until sold out
- **WHEN** a page announces a fan-club first-come sale that opens tomorrow at 18:30 and ends when tickets run out
- **THEN** that sale is not returned

#### Scenario: Lottery without a stated close
- **WHEN** a page announces a lottery with a start date and no end date
- **THEN** that sale is not returned

#### Scenario: Sale without a name
- **WHEN** a page announces a sale's period without naming the sale
- **THEN** that sale is not returned

## REMOVED Requirements

### Requirement: Required values come from the source pages

**Reason**: The lottery result time is no longer read, and a sale without a stated end time or name is no longer returned.
**Migration**: See "A sale is returned only with its name, method, start and end from the pages".
