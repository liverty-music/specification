## ADDED Requirements

### Requirement: A window is local date-times in one time zone

Create and SetWindow SHALL take the sale's start time and end time each as a local date-time, a calendar date and a time of day, together with one IANA time zone in which both are read; the sale is created, or its window is set, in that time zone. Each call SHALL fail with InvalidArgument, before any usecase runs, when the time zone is missing or is not an IANA time zone name, when a start or end time is given with a UTC offset instead of the time zone, or when the start time and the end time name different time zones, or when a start or end time has a month, day, hour or minute out of range, a second or a fraction of a second, or a day that does not exist in its month (30 February). A local date-time that does not exist in the time zone is rejected by the TicketSale rules through the usecase, and its InvalidArgument is returned unchanged. Every sale the boundary returns SHALL carry its start time and end time as local date-times with its time zone.

#### Scenario: Sale for a show abroad

- **WHEN** a member calls Create for a Lottery sale from 2026-11-01 12:00 to 2026-11-07 23:59 in the time zone Asia/Taipei
- **THEN** the sale is created in Asia/Taipei and returned with the start 2026-11-01 12:00 and the end 2026-11-07 23:59, each with the time zone Asia/Taipei

#### Scenario: Time with seconds or a day that does not exist
- **WHEN** Create is called with a start time of 2027-02-30 12:00, or with an end time of 2027-03-01 12:00:30
- **THEN** it fails with InvalidArgument before any usecase runs and nothing is stored

#### Scenario: Window without a time zone

- **WHEN** SetWindow is called with a start and an end time and no time zone
- **THEN** it fails with InvalidArgument and nothing changes

#### Scenario: Offset instead of a time zone

- **WHEN** Create is called with a start time given as 2026-11-01 12:00 at UTC+09:00
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: Start and end in different time zones

- **WHEN** Create is called with a start time in Asia/Tokyo and an end time in Asia/Seoul
- **THEN** it fails with InvalidArgument and nothing is created

#### Scenario: Time skipped by the clock change

- **WHEN** SetWindow is called with a start time of 2027-03-14 02:30 in the time zone America/New_York, a time the clocks skip that night
- **THEN** the usecase's InvalidArgument is returned and nothing changes
