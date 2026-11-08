# components/entity/notification/list-by-user Specification

## Purpose
Returns a fan's newest Notifications, newest first, up to a given number, for the fan's notification center.

## Requirements

### Requirement: ListByUser returns the fan's newest notifications

ListByUser SHALL return the Notifications of the given fan, newest create time first, at most the given limit, with all their attributes. Another fan's Notifications SHALL never be returned. A fan with no Notification SHALL get an empty list without an error. A limit below 1 SHALL fail with InvalidArgument.

#### Scenario: More than the limit
- **WHEN** a fan has 60 Notifications and ListByUser runs with the limit 50
- **THEN** the 50 newest are returned, newest first

#### Scenario: Another fan's notifications
- **WHEN** two fans each have Notifications
- **THEN** ListByUser for one fan returns none of the other's

#### Scenario: No notification
- **WHEN** the fan has no Notification
- **THEN** an empty list is returned

#### Scenario: Zero limit
- **WHEN** ListByUser runs with the limit 0
- **THEN** it fails with InvalidArgument
