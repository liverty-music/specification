## ADDED Requirements

### Requirement: Search covers the artist's own shows

Search SHALL return only the solo shows, co-headliner bills (対バン) and tours organized by the Artist. Music festivals and other multi-artist events at which the Artist is one of many performers SHALL be left out, and so SHALL shows announced as 中止 (cancelled).

#### Scenario: Festival left out
- **WHEN** the source lists the Artist among the lineup of a multi-artist music festival
- **THEN** Search does not return the festival

#### Scenario: Cancelled show left out
- **WHEN** the source lists a show of the Artist as 中止 (cancelled)
- **THEN** Search does not return it

#### Scenario: Co-headliner bill organized by the artist
- **WHEN** the source lists a two-act bill organized by the Artist
- **THEN** Search returns it as a SINGLE series

## MODIFIED Requirements

### Requirement: Search removes repeated events

Search SHALL return at most one event per local date, normalized venue name and start time, keeping the first; two events at one venue on one date with different start times SHALL both be returned, and two with no start time SHALL collapse to one. Venue names that differ only in notation SHALL normalize to the same name: full-width versus half-width characters, compatibility characters (such as the radical ⽇ for 日), middle-dot variants, and whitespace.

#### Scenario: First and second stage kept
- **WHEN** the source lists 2026-08-07 at one venue at 18:00 and at 21:00
- **THEN** Search returns both events

#### Scenario: Identical event listed twice
- **WHEN** the source lists the same date, venue and start time twice
- **THEN** Search returns it once

#### Scenario: Same venue in two notations
- **WHEN** the source lists one date and start time once at "渋谷CLUB QUATTRO" and once at "渋谷 CLUB QUATTRO"
- **THEN** Search returns it once

### Requirement: Search returns source text as written

Search SHALL return each event's venue name as the source wrote it, in its original language, without translating or romanizing it and without replacing it with another name for the same venue; annotations the source includes, such as a former name in parentheses, SHALL be kept. Each series' source page SHALL be the page dedicated to that tour when one exists, otherwise the official site's detail page for the concert. A date written without a year SHALL be returned with the year inferred from the page's context.

#### Scenario: Japanese venue on a multilingual page
- **WHEN** the source writes the venue as "幕張メッセ 9・11ホール" and also offers an English view
- **THEN** Search returns "幕張メッセ 9・11ホール"

#### Scenario: Former name kept
- **WHEN** the source writes the venue as "クロコくんホール（旧 日本ガイシホール）"
- **THEN** Search returns "クロコくんホール（旧 日本ガイシホール）", not "日本ガイシホール"

#### Scenario: Year inferred from a two-year tour title
- **WHEN** a page titled "TOUR 2026-2027" lists "01.16. sat" after dates in 2026
- **THEN** Search returns 2027-01-16

### Requirement: Admin area is an ISO code or absent

Search SHALL return a venue's admin area only when the source states it or the venue makes it unambiguous, and only as the ISO 3166-2 code of the venue's first-level subdivision, for a venue in any country. An area already given as an ISO 3166-2 code SHALL be returned upper-cased; Japan's 47 prefectures written in Japanese with or without their suffix, or in English in any case, SHALL be returned as their code. Anything else SHALL be returned as no admin area.

#### Scenario: Prefecture in Japanese
- **WHEN** the source gives the admin area "愛知県"
- **THEN** Search returns JP-23

#### Scenario: Prefecture in English
- **WHEN** the source gives the admin area "tokyo"
- **THEN** Search returns JP-13

#### Scenario: Overseas venue
- **WHEN** the show is at Taipei Arena in Taipei
- **THEN** Search returns TW-TPE

#### Scenario: Unrecognized area
- **WHEN** the source gives the admin area "California" in free text
- **THEN** Search returns no admin area

### Requirement: Transient failures degrade to no results

Search SHALL retry a transient external failure — a timeout, rate limit, server error, temporary authorization failure or incomplete response — for up to 3 attempts in total. When every attempt fails transiently, Search SHALL return no concerts and no error. A permanent failure, a structurally broken response, a response that carries no candidate result, or the caller's own deadline or cancellation SHALL fail Search with an error; a response with no candidate result SHALL NOT be retried within the same Search.

#### Scenario: Recovered on retry
- **WHEN** the first attempt times out and the second succeeds
- **THEN** Search returns the second attempt's concerts

#### Scenario: All attempts transient
- **WHEN** all 3 attempts are rate-limited
- **THEN** Search returns no concerts and no error

#### Scenario: Response without a candidate
- **WHEN** the external service answers successfully but with no candidate result
- **THEN** Search fails with an error after that one attempt

#### Scenario: Caller deadline expires
- **WHEN** the caller's deadline expires during Search
- **THEN** Search fails with an error
