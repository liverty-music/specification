# List Followed

## Purpose

FollowUseCase.ListFollowed returns the artists a fan follows, each with the fan's hype level for it.

## Requirements

### Requirement: ListFollowed returns the fan's follows

ListFollowed SHALL return the fan's followed artists with their hype levels as Follow.ListByUser returns them, in no particular order. A fan who follows nobody SHALL get an empty list.

#### Scenario: Fan follows three artists

- **WHEN** a fan follows three artists at different hype levels
- **THEN** ListFollowed returns the three artists, each with its own hype level

#### Scenario: Fan follows nobody

- **WHEN** a fan has no Follow
- **THEN** ListFollowed returns an empty list
