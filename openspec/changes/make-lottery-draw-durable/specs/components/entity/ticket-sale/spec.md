## MODIFIED Requirements

### Requirement: Result time of a lottery

A Lottery sale's result time SHALL be its lottery result time when it has one. An Organizer's Lottery sale's result time SHALL be its end time, because its draw starts once the end time has passed and each fan is told the result. A discovered Lottery sale without a lottery result time SHALL have no result time. A FirstCome sale SHALL have no result time.

#### Scenario: Discovered lottery with an announced result
- **WHEN** a discovered Lottery sale closes on 22 October 23:59 and has the lottery result time 3 November 15:00
- **THEN** its result time is 3 November 15:00

#### Scenario: Organizer's lottery
- **WHEN** an Organizer's Lottery sale ends on 22 October 23:59
- **THEN** its result time is 22 October 23:59

#### Scenario: Discovered lottery without an announced result
- **WHEN** a discovered Lottery sale has no lottery result time
- **THEN** it has no result time
