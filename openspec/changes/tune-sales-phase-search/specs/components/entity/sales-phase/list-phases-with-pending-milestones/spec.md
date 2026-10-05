# Spec Delta

## MODIFIED Requirements

### Requirement: Phases are selected by opening time and latest milestone

ListPhasesWithPendingMilestones SHALL return every sales phase whose apply start time is no later than now plus the lookahead, and whose latest known milestone among apply start time, apply end time and lottery result time is no earlier than now minus the lookback, ordered by apply start time, earliest first.

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
