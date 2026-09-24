# Concert.FillEventStartTimes

## Purpose

Fills unknown start and open times on existing Events when a later source supplies them.

## Requirements

### Requirement: Fill only unknown times

FillEventStartTimes SHALL set each given Event's start time and open time only where the Event's value is unknown; a known time SHALL never be overwritten, and an unknown supplied time leaves the Event unchanged. An unknown Event id SHALL be ignored, and an empty request SHALL change nothing.

#### Scenario: Unknown start filled
- **WHEN** an Event has no start time and 18:00 is supplied
- **THEN** the Event starts at 18:00

#### Scenario: Known start kept
- **WHEN** an Event starts at 18:00 and 19:00 is supplied
- **THEN** the Event still starts at 18:00

#### Scenario: Repeated fill
- **WHEN** the same fill is applied twice
- **THEN** the second application changes nothing
