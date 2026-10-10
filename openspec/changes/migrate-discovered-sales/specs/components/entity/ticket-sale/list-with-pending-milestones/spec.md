# Spec Delta

## Purpose

ListWithPendingMilestones returns the TicketSales, discovered or an Organizer's, that may still have a reminder milestone to act on: sales that open within a given lookahead and whose latest milestone is not further in the past than a given lookback.

## ADDED Requirements

### Requirement: Sales are selected by start time and latest milestone

ListWithPendingMilestones SHALL return every TicketSale whose start time is no later than now plus the lookahead, and whose latest known milestone among start time, end time and result time is no earlier than now minus the lookback, ordered by start time, earliest first, each with its TicketTypes. An Organizer's sale SHALL be returned only while its Series is Published.

#### Scenario: Opened weeks ago, result tomorrow
- **WHEN** a discovered lottery opened 3 weeks ago and its result time is tomorrow
- **THEN** the sale is returned

#### Scenario: Opens beyond the lookahead
- **WHEN** the lookahead is 7 days and a sale opens in 10 days
- **THEN** the sale is not returned

#### Scenario: All milestones long past
- **WHEN** the lookback is 2 hours and the latest milestone of a sale was 3 hours ago
- **THEN** the sale is not returned

#### Scenario: Latest milestone just past
- **WHEN** the lookback is 2 hours and the latest milestone of a sale was 1 hour ago
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

### Requirement: The window arguments are validated

ListWithPendingMilestones SHALL fail with InvalidArgument when the lookahead is not positive or the lookback is negative.

#### Scenario: Zero lookahead
- **WHEN** ListWithPendingMilestones is called with a lookahead of 0
- **THEN** it fails with InvalidArgument

#### Scenario: Negative lookback
- **WHEN** ListWithPendingMilestones is called with a lookback of -1 hour
- **THEN** it fails with InvalidArgument
