## ADDED Requirements

### Requirement: Every sale has a time zone

Every TicketSale SHALL have a time zone, the IANA time zone name in which its start and end are announced, such as Asia/Taipei. A sale without a time zone, or with a name that is not a time zone of the IANA time zone database, SHALL be invalid; an abbreviation or a UTC offset is not a time zone.

#### Scenario: Sale in Taipei
- **WHEN** a sale's time zone is Asia/Taipei
- **THEN** the time zone is valid

#### Scenario: Abbreviation instead of a zone
- **WHEN** a sale's time zone is JST or +09:00
- **THEN** the sale is invalid

#### Scenario: No time zone
- **WHEN** a sale has no time zone
- **THEN** the sale is invalid

### Requirement: The window is local date-times in the sale's time zone

A TicketSale's start time and end time SHALL each be a local date-time, a calendar date and a time of day without an offset, read in the sale's time zone. The instant of each SHALL be computed from the local date-time and the sale's time zone whenever a rule needs one, so a change of the zone's rules before the sale moves the instant and keeps the announced wall-clock time. Every rule that compares a sale's start or end with an instant, with another sale's window or with an event's start SHALL use these instants; the length of an Organizer's Lottery window is measured on the local date-times instead ("A lottery window lasts 1 to 14 days"). A local date-time that does not exist in the sale's time zone, because the clocks skip it when daylight saving time starts, SHALL be invalid. A local date-time that occurs twice, because the clocks repeat it when daylight saving time ends, SHALL stand for the earlier of the two instants. A start time and an end time SHALL be in whole minutes, with no seconds or fraction.

#### Scenario: Times are whole minutes
- **WHEN** a sale is stored with an end time of 2026-11-10 20:00:30
- **THEN** the sale is invalid

#### Scenario: Sale abroad
- **WHEN** a sale's time zone is Asia/Taipei and its start time is 2026-11-01 12:00
- **THEN** the sale opens at the instant 2026-11-01 04:00 UTC, which is 13:00 in Japan time

#### Scenario: Start in the spring-forward gap
- **WHEN** a sale's time zone is America/New_York and its start time is 2027-03-14 02:30, which the clocks skip that night
- **THEN** the sale is invalid

#### Scenario: End in the repeated hour
- **WHEN** a sale's time zone is America/New_York and its end time is 2026-11-01 01:30, which occurs twice that night
- **THEN** the sale closes at the instant 2026-11-01 05:30 UTC, the first 01:30

#### Scenario: Windows in two time zones
- **WHEN** one sale in Asia/Tokyo ends at 2026-11-10 20:00 and another sale in Asia/Taipei starts at 2026-11-10 19:30, which is 20:30 in Japan time
- **THEN** the windows do not overlap

## MODIFIED Requirements

### Requirement: A lottery window lasts 1 to 14 days

A TicketSale's end time SHALL be after its start time. When an Organizer's sale has the method Lottery, its window SHALL last at least 1 day and at most 14 days, measured on its local date-times in the sale's time zone as the wall clock shows them, so a clock change inside the window neither shortens nor lengthens it. A discovered sale's window SHALL have no limit on its length.

#### Scenario: Lottery window within bounds
- **WHEN** an Organizer's Lottery sale runs for 10 days
- **THEN** the window is valid

#### Scenario: Lottery window shorter than 1 day
- **WHEN** an Organizer's Lottery sale runs for 23 hours
- **THEN** the window is invalid

#### Scenario: Lottery window longer than 14 days
- **WHEN** an Organizer's Lottery sale runs for 14 days and 1 hour
- **THEN** the window is invalid

#### Scenario: One day across the clock change
- **WHEN** an Organizer's Lottery sale in Europe/London runs from 2027-03-27 12:00 to 2027-03-28 12:00, although only 23 hours pass because the clocks go forward on 28 March
- **THEN** the window lasts 1 day and is valid

#### Scenario: End not after start
- **WHEN** the end time equals or precedes the start time
- **THEN** the window is invalid

#### Scenario: Discovered lottery longer than 14 days
- **WHEN** a discovered Lottery sale runs from 1 October to 31 October
- **THEN** the window is valid

#### Scenario: First-come window longer than 14 days
- **WHEN** a FirstCome sale runs from 2026-11-01 10:00 to 2026-11-20 18:00
- **THEN** the window is valid

### Requirement: Only a discovered lottery has a result date

A TicketSale's result date SHALL be the calendar day on which the lottery's results are announced, as its source states it; it is a date without a time of day or a time zone. Only a discovered Lottery sale MAY have one, and it SHALL be no earlier than the calendar day of the sale's end time, which is the date of its local end date-time in the sale's time zone. A sale without a result date is valid.

#### Scenario: Discovered lottery with a result date

- **WHEN** a discovered lottery closes on 22 October 23:59 and its result date is 3 November
- **THEN** the sale is valid

#### Scenario: Result date before the close

- **WHEN** a discovered lottery closes on 22 October 23:59 and its result date is 20 October
- **THEN** the sale is invalid

#### Scenario: Result date on the closing day abroad

- **WHEN** a discovered lottery in Europe/London closes on 22 October 23:30, which is 23 October in Japan time, and its result date is 22 October
- **THEN** the sale is valid

#### Scenario: First-come sale with a result date

- **WHEN** a discovered first-come sale has a result date
- **THEN** the sale is invalid

#### Scenario: Organizer's lottery with a result date

- **WHEN** an Organizer's lottery has a result date
- **THEN** the sale is invalid

#### Scenario: Discovered lottery without a result date

- **WHEN** a discovered lottery has no result date
- **THEN** the sale is valid
