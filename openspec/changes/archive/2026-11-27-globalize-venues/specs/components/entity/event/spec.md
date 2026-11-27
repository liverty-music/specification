## ADDED Requirements

### Requirement: Start and open times are times of day at the Venue

An Event's start time and open time SHALL each be a time of day on its local date, read in the time zone of its Venue. The instant of the start SHALL be computed from the local date, the start time and the Venue's time zone whenever a rule needs one, so a change of the zone's rules before the event moves the instant and keeps the announced wall-clock time. A start or open time that does not exist on the local date in the Venue's time zone, because the clocks skip it when daylight saving time starts, SHALL be invalid. A start time that occurs twice on the local date, because the clocks repeat it when daylight saving time ends, SHALL stand for the earlier of the two instants.

#### Scenario: Show in Seoul
- **WHEN** an Event at a Venue in Asia/Seoul is on 2027-03-14 and starts at 18:30
- **THEN** its start is the instant 2027-03-14 09:30 UTC, which is 18:30 in Japan time

#### Scenario: Show in London
- **WHEN** an Event at a Venue in Europe/London is on 2026-11-10 and starts at 19:30
- **THEN** its start is the instant 2026-11-10 19:30 UTC, which is 04:30 on 11 November in Japan time

#### Scenario: Start in the spring-forward gap
- **WHEN** an Event at a Venue in America/New_York is on 2027-03-14 and starts at 02:30, which the clocks skip that night
- **THEN** the Event is invalid

#### Scenario: Start in the repeated hour
- **WHEN** an Event at a Venue in America/New_York is on 2026-11-01 and starts at 01:30, which occurs twice that night
- **THEN** its start is the instant 2026-11-01 05:30 UTC, the first 01:30
