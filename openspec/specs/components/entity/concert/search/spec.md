# Concert.Search

## Purpose

Searches external sources for an Artist's announced concerts from a given date onward and returns them as DiscoveredSeries, grounded on the Artist's name and, when known, its official site.

## Requirements

### Requirement: Search returns grouped future events

Search SHALL return the Artist's concerts dated on or after the given date as DiscoveredSeries: each tour as one TOUR series and each standalone show as its own SINGLE series, even when two standalone shows share a title. Events dated before the given date SHALL be left out. An Artist with no official site SHALL still be searched by name.

#### Scenario: Past event left out
- **WHEN** the source lists a show dated before the given date
- **THEN** Search does not return it

#### Scenario: Two standalone shows with one title
- **WHEN** the source lists two standalone shows with the same title
- **THEN** Search returns two SINGLE series

#### Scenario: No official site
- **WHEN** the Artist has no official site
- **THEN** Search still searches by the Artist's name

### Requirement: Search removes repeated events

Search SHALL return at most one event per local date, normalized venue name and start time, keeping the first; two events at one venue on one date with different start times SHALL both be returned, and two with no start time SHALL collapse to one.

#### Scenario: First and second stage kept
- **WHEN** the source lists 2026-08-07 at one venue at 18:00 and at 21:00
- **THEN** Search returns both events

#### Scenario: Identical event listed twice
- **WHEN** the source lists the same date, venue and start time twice
- **THEN** Search returns it once

### Requirement: Search returns source text as written

Search SHALL return each event's venue name as the source wrote it, without translating or romanizing it, and each series' source page as the page dedicated to that tour or show when one exists, otherwise the most detailed official page available. A date written without a year SHALL be returned with the year inferred from the page's context.

#### Scenario: Japanese venue on a multilingual page
- **WHEN** the source writes the venue as "幕張メッセ 9・11ホール" and also offers an English view
- **THEN** Search returns "幕張メッセ 9・11ホール"

#### Scenario: Year inferred from a two-year tour title
- **WHEN** a page titled "TOUR 2026-2027" lists "01.16. sat" after dates in 2026
- **THEN** Search returns 2027-01-16

### Requirement: Admin area is an ISO code or absent

Search SHALL return a venue's admin area only when the source states it or the venue name makes it unambiguous, and only as an ISO 3166-2 code; only Japan's 47 prefectures, written in Japanese with or without their suffix or in English in any case, are recognized. Anything else SHALL be returned as no admin area.

#### Scenario: Prefecture in Japanese
- **WHEN** the source gives the admin area "愛知県"
- **THEN** Search returns JP-23

#### Scenario: Prefecture in English
- **WHEN** the source gives the admin area "tokyo"
- **THEN** Search returns JP-13

#### Scenario: Unrecognized area
- **WHEN** the source gives the admin area "California"
- **THEN** Search returns no admin area

### Requirement: Unknown times are absent

Search SHALL return a start or open time only when the source gives a parseable time; a missing, "null" or unparseable time SHALL be returned as unknown. An event whose date cannot be parsed SHALL be left out.

#### Scenario: Literal null start
- **WHEN** the source's start time reads "null"
- **THEN** the event has no start time

### Requirement: Transient failures degrade to no results

Search SHALL retry a transient external failure — a timeout, rate limit, server error, temporary authorization failure or incomplete response — for up to 3 attempts in total. When every attempt fails transiently, Search SHALL return no concerts and no error. A permanent failure, a structurally broken response, or the caller's own deadline or cancellation SHALL fail Search with an error.

#### Scenario: Recovered on retry
- **WHEN** the first attempt times out and the second succeeds
- **THEN** Search returns the second attempt's concerts

#### Scenario: All attempts transient
- **WHEN** all 3 attempts are rate-limited
- **THEN** Search returns no concerts and no error

#### Scenario: Caller deadline expires
- **WHEN** the caller's deadline expires during Search
- **THEN** Search fails with an error
