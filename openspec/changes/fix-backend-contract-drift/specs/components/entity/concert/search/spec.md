## MODIFIED Requirements

### Requirement: Search returns grouped future events

Search SHALL return the Artist's concerts whose local date is on or after the current date at their Venue at the given time (see Venue) as DiscoveredSeries, one per tour or show, and two separately announced shows SHALL be two series even when they share a title. A series whose events are at two or more venues SHALL be a TOUR series; any other series, a one-off show or several days at one venue, SHALL be a SINGLE series. A venue not yet announced SHALL NOT count as a venue. Events dated before the current date at their Venue SHALL be left out. An Artist with no official site SHALL still be searched by name.

#### Scenario: Past event left out
- **WHEN** the source lists a show dated before the current date at its Venue
- **THEN** Search does not return it

#### Scenario: Yesterday's show early in the morning
- **WHEN** Search runs at 2026-11-10 23:30 UTC, which is 2026-11-11 at the Venue, and the source lists a show dated 2026-11-10
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

### Requirement: Search removes repeated events

Search SHALL return at most one event per local date, venue name and start time, keeping the first; two events at one venue on one date with different start times SHALL both be returned, and two with no start time SHALL collapse to one. Two venue names SHALL be the same when their normalized forms (see Venue, "Listed venue name normalization") are equal ignoring whitespace, middle-dot variants and Latin letter case; this covers full-width versus half-width characters, compatibility characters (such as the radical ⽇ for 日), middle-dot variants, whitespace and letter case. No other rule, such as a list of renamed venues or a prefecture in parentheses, SHALL make two venue names the same.

#### Scenario: First and second stage kept
- **WHEN** the source lists 2026-08-07 at one venue at 18:00 and at 21:00
- **THEN** Search returns both events

#### Scenario: Identical event listed twice
- **WHEN** the source lists the same date, venue and start time twice
- **THEN** Search returns it once

#### Scenario: Same venue in two notations
- **WHEN** the source lists one date and start time once at "渋谷CLUB QUATTRO" and once at "渋谷 CLUB QUATTRO"
- **THEN** Search returns it once

#### Scenario: Same venue in another letter case
- **WHEN** the source lists one date and start time once at "Zepp Haneda" and once at "ZEPP HANEDA"
- **THEN** Search returns it once
