# components/usecase/area/resolve Specification

## Purpose
AreaUseCase.Resolve tells an admin which first-level Area an entered area text stands for, with its country and time zone, so the approval queue can offer that country's time zones before the admin approves a discovered concert.

## Requirements

### Requirement: The first-level Area an entered text stands for

Resolve SHALL take a text and an optional country code, and return the result of Area.Resolve for them unchanged: the first-level Area with its code, kind, country code, English name, Japanese name when it has one and time zone when it has one, or the same NotFound and InvalidArgument failures. It SHALL store nothing.

#### Scenario: Name of a state

- **WHEN** Resolve is called with `California`
- **THEN** the Area `US-CA` is returned with country code `US` and the time zone `America/Los_Angeles`

#### Scenario: Lower-level code

- **WHEN** Resolve is called with `FR-33`
- **THEN** the Area `FR-NAQ` is returned

#### Scenario: Text that stands for no Area

- **WHEN** Area.Resolve fails with NotFound for `JP-99`
- **THEN** Resolve fails with NotFound
