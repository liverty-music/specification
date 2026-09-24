# PushSubscription.ListByUserIDs

## Purpose

Lists every PushSubscription held by any of the given fans.

## Requirements

### Requirement: ListByUserIDs returns all subscriptions of the given fans

ListByUserIDs SHALL return every PushSubscription whose owner is one of the given fans, in no particular order. When none of them has a PushSubscription, or no fan is given, it SHALL return an empty list, not an error.

#### Scenario: Fan with two browsers

- **WHEN** ListByUserIDs runs for a fan with two registered browsers
- **THEN** both PushSubscriptions are returned

#### Scenario: No subscriptions

- **WHEN** none of the given fans has a PushSubscription
- **THEN** an empty list is returned

#### Scenario: No fans given

- **WHEN** the list of fans is empty
- **THEN** an empty list is returned
