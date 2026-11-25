## MODIFIED Requirements

### Requirement: Search returns grouped future events

Search SHALL return the Artist's concerts whose local date is on or after the current date at their Venue at the given time (see Venue) as DiscoveredSeries, one per tour or show, and two separately announced shows SHALL be two series even when they share a title. A series whose events are at two or more venues SHALL be a TOUR series; any other series, a one-off show or several days at one venue, SHALL be a SINGLE series. A venue not yet announced SHALL NOT count as a venue. Events dated before the current date at their Venue SHALL be left out, the Venue's time zone being the event's time zone (see "Time zone of each event"). An event whose time zone is unknown SHALL be left out only when its local date is before the current date in every time zone, that is, before the date at UTC−12 at the given time, so it is never left out while its date may still be today or later where it takes place. An Artist with no official site SHALL still be searched by name.

#### Scenario: Past event left out
- **WHEN** the source lists a show dated before the current date at its Venue
- **THEN** Search does not return it

#### Scenario: Yesterday's show early in the morning
- **WHEN** Search runs at 2026-11-10 23:30 UTC, which is 2026-11-11 at the Venue, and the source lists a show dated 2026-11-10
- **THEN** Search does not return it

#### Scenario: Time zone unknown, date possibly still today
- **WHEN** Search runs at 2026-11-11 08:00 UTC, which is 2026-11-10 at UTC−12, and the source lists a show dated 2026-11-10 whose time zone is unknown
- **THEN** Search returns it

#### Scenario: Time zone unknown, date past everywhere
- **WHEN** Search runs at 2026-11-11 13:00 UTC, which is 2026-11-11 at UTC−12, and the source lists a show dated 2026-11-10 whose time zone is unknown
- **THEN** Search does not return it

#### Scenario: Two standalone shows with one title
- **WHEN** the source lists two separately announced one-off shows with the same title
- **THEN** Search returns two SINGLE series

#### Scenario: Tour across venues
- **WHEN** the source lists a tour with dates at Zepp Nagoya and Taipei Arena
- **THEN** Search returns one TOUR series with both events

#### Scenario: Two days at one venue
- **WHEN** the source lists one show on 2026-11-25 and 2026-11-26 at LaLa arena TOKYO-BAY
- **THEN** Search returns one SINGLE series with both events

#### Scenario: No official site
- **WHEN** the Artist has no official site
- **THEN** Search still searches by the Artist's name

### Requirement: Search covers the artist's own shows

Search SHALL return only the solo shows, co-headliner bills (対バン) and tours organized by the Artist. Music festivals and other multi-artist events at which the Artist is one of many performers SHALL be left out, and so SHALL shows announced as 中止 (cancelled), and any show a fan cannot go to at one fixed, named place, because a show is listed under the city and time zone of its venue: a private or invited-guests-only event, an online-only show, or a show held on a ship or an aircraft.

#### Scenario: Festival left out
- **WHEN** the source lists the Artist among the lineup of a multi-artist music festival
- **THEN** Search does not return the festival

#### Scenario: Cancelled show left out
- **WHEN** the source lists a show of the Artist as 中止 (cancelled)
- **THEN** Search does not return it

#### Scenario: Co-headliner bill organized by the artist
- **WHEN** the source lists a two-act bill organized by the Artist
- **THEN** Search returns it as a SINGLE series

#### Scenario: Private event left out
- **WHEN** the source lists a show of the Artist with the venue "PRIVATE"
- **THEN** Search does not return it

#### Scenario: Online-only show left out
- **WHEN** the source lists a show of the Artist that is streamed and has no venue
- **THEN** Search does not return it

#### Scenario: Show on a cruise ship left out
- **WHEN** the source lists a show of the Artist on the pool deck of a cruise ship during a voyage
- **THEN** Search does not return it

### Requirement: Admin area is an ISO code or absent

Search SHALL return a venue's admin area only when the source states it or the venue makes it unambiguous, for a venue in any country, and only as the code of the first-level Area that the area resolves to without a country (see Area.Resolve): a code of any level or letter case, or an English or Japanese name. An area that does not resolve SHALL be returned as no admin area.

#### Scenario: Prefecture in Japanese
- **WHEN** the source gives the admin area "愛知県"
- **THEN** Search returns JP-23

#### Scenario: Prefecture in English
- **WHEN** the source gives the admin area "tokyo"
- **THEN** Search returns JP-13

#### Scenario: Overseas venue
- **WHEN** the show is at Taipei Arena in Taipei
- **THEN** Search returns TW-TPE

#### Scenario: State name
- **WHEN** the source gives the admin area "California" in free text
- **THEN** Search returns US-CA

#### Scenario: Lower-level code
- **WHEN** the area found for a venue in Bordeaux is FR-33
- **THEN** Search returns FR-NAQ

#### Scenario: Territory without subdivisions
- **WHEN** the show is at AsiaWorld-Arena in Hong Kong, given as HK or as CN-HK
- **THEN** Search returns HK

#### Scenario: Unrecognized area
- **WHEN** the source gives the admin area "Atlantis", or a well-formed code that is no Area such as JP-99
- **THEN** Search returns no admin area

#### Scenario: Name of areas in two countries
- **WHEN** the source gives the admin area "Victoria" and nothing else tells the country
- **THEN** Search returns no admin area

### Requirement: Unknown times are absent

Search SHALL return each event's start and open time as a time of day at the venue (hours and minutes), as the source states it, without converting it to another time zone, and only when the source gives a parseable time; a missing, "null" or unparseable time SHALL be returned as unknown. A time that does not exist on the event's date in the event's time zone, because a daylight saving change skips it, SHALL be returned as unknown. An event whose date cannot be parsed SHALL be left out.

#### Scenario: Literal null start
- **WHEN** the source's start time reads "null"
- **THEN** the event has no start time

#### Scenario: Show abroad keeps its local time
- **WHEN** the source lists a show in Seoul with "OPEN 17:30 / START 18:30"
- **THEN** Search returns the open time 17:30 and the start time 18:30

#### Scenario: Time skipped by daylight saving
- **WHEN** the source lists a show on 2027-03-14 starting at 02:30 at a venue whose time zone is America/New_York
- **THEN** the event has no start time

## ADDED Requirements

### Requirement: Time zone of each event

Search SHALL return each event's time zone as an IANA time zone name: the time zone of its admin area's Area when that Area has one; otherwise the time zone the source implies, when it is one of the time zones of the admin area's country; otherwise none. An event without an admin area SHALL have no time zone.

#### Scenario: Area with one time zone
- **WHEN** the event's admin area is JP-23
- **THEN** its time zone is Asia/Tokyo

#### Scenario: Area without a single time zone
- **WHEN** the event's admin area is US-TX, which has no time zone of its own, and the source implies America/Chicago
- **THEN** its time zone is America/Chicago

#### Scenario: Zone of another country
- **WHEN** the event's admin area is US-TX and the source implies Europe/London
- **THEN** the event has no time zone

#### Scenario: Area unknown
- **WHEN** the event has no admin area
- **THEN** the event has no time zone
