# Spec Delta

## Purpose

Lists the Settlements whose release is under way, with their release claims, so a release that was claimed but not started can be started.

## ADDED Requirements

### Requirement: Releasing settlements

ListReleasing SHALL return every Releasing Settlement with its release claim and splits, oldest first. It SHALL return an empty list when none is Releasing.

#### Scenario: One releasing
- **WHEN** one Settlement is Releasing and one is Held
- **THEN** only the Releasing Settlement is returned, with its release claim

#### Scenario: None releasing
- **WHEN** no Settlement is Releasing
- **THEN** an empty list is returned
