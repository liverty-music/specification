# SalesPhase.ListPhasesWithPendingMilestones

## Purpose

ListPhasesWithPendingMilestones returns the sales phases that may still have a reminder milestone to act on: phases that open within a given lookahead and whose latest milestone is not further in the past than a given lookback.

## Requirements

### Requirement: Phases are selected by opening time and latest milestone

ListPhasesWithPendingMilestones SHALL return every sales phase whose apply start time is no later than now plus the lookahead, and whose latest known milestone among apply start time, apply end time and lottery result time is no earlier than now minus the lookback, ordered by apply start time, earliest first. The payment deadline time SHALL NOT count as a milestone.

#### Scenario: Opened weeks ago, result tomorrow

- **WHEN** a phase opened 3 weeks ago and its lottery result time is tomorrow
- **THEN** the phase is returned

#### Scenario: Opens beyond the lookahead

- **WHEN** the lookahead is 7 days and a phase opens in 10 days
- **THEN** the phase is not returned

#### Scenario: All milestones long past

- **WHEN** the lookback is 2 hours and the latest milestone of a phase was 3 hours ago
- **THEN** the phase is not returned

#### Scenario: Latest milestone just past

- **WHEN** the lookback is 2 hours and the latest milestone of a phase was 1 hour ago
- **THEN** the phase is returned

#### Scenario: Nothing pending

- **WHEN** no phase meets both conditions
- **THEN** ListPhasesWithPendingMilestones returns an empty list without an error

### Requirement: The window arguments are validated

ListPhasesWithPendingMilestones SHALL fail with InvalidArgument when the lookahead is not positive or the lookback is negative.

#### Scenario: Zero lookahead

- **WHEN** ListPhasesWithPendingMilestones is called with a lookahead of 0
- **THEN** it fails with InvalidArgument

#### Scenario: Negative lookback

- **WHEN** ListPhasesWithPendingMilestones is called with a lookback of -1 hour
- **THEN** it fails with InvalidArgument
