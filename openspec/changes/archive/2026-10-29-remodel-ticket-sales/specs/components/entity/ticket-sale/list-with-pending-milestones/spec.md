# Spec Delta

## ADDED Requirements

### Requirement: Sales are selected by start time and end time

ListWithPendingMilestones SHALL return every TicketSale whose start time is no later than now plus the lookahead, and whose end time is no earlier than now minus the lookback, ordered by start time, earliest first, each with the events it names. An Organizer's sale SHALL be returned only while its Series is Published.

#### Scenario: Opened days ago, closes tomorrow
- **WHEN** a lottery opened 10 days ago and its end time is tomorrow
- **THEN** the sale is returned

#### Scenario: Opens beyond the lookahead
- **WHEN** the lookahead is 7 days and a sale opens in 10 days
- **THEN** the sale is not returned

#### Scenario: All milestones long past
- **WHEN** the lookback is 2 hours and a sale's end time was 3 hours ago
- **THEN** the sale is not returned

#### Scenario: Latest milestone just past
- **WHEN** the lookback is 2 hours and a sale's end time was 1 hour ago
- **THEN** the sale is returned

#### Scenario: Organizer's sale opening tomorrow
- **WHEN** an Organizer's lottery of a Published Series opens tomorrow
- **THEN** the sale is returned

#### Scenario: Organizer's sale of a cancelled Series
- **WHEN** an Organizer's lottery opens tomorrow and its Series is Cancelled
- **THEN** the sale is not returned

#### Scenario: Nothing pending
- **WHEN** no sale meets the conditions
- **THEN** ListWithPendingMilestones returns an empty list without an error

## REMOVED Requirements

### Requirement: Sales are selected by start time and latest milestone

**Reason**: Every sale has an end time, and with the lottery result time removed its latest milestone is its end time.
**Migration**: See "Sales are selected by start time and end time".
