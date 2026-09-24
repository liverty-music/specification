# SalesPhase.SearchSalesPhases

## Purpose

SearchSalesPhases looks up, in one search per artist, the ticket sales a fan can still apply for across the artist's upcoming series, reading the artist's official site and the ticket pages it links to, and returns each sale found as a discovered phase attributed to one of those series. Extraction is best-effort: its results are verified by an integration test against real pages, not guaranteed per page.

## Requirements

### Requirement: One search covers all of an artist's upcoming series

SearchSalesPhases SHALL take the artist, the artist's official site, and the artist's upcoming series (each with its title and known event dates), and SHALL return discovered phases, each attributed to exactly one of the given series. A sale that cannot be attributed to one of the given series SHALL be discarded. The search SHALL NOT resolve which events of a series a phase covers. When no series is given, SearchSalesPhases SHALL return no phases without searching.

#### Scenario: Artist with two tours

- **WHEN** SearchSalesPhases runs for an artist with two upcoming series and the official site lists a presale for each
- **THEN** it returns two discovered phases, each attributed to its own series

#### Scenario: Unattributable sale

- **WHEN** the official site lists a sale that matches none of the given series
- **THEN** that sale is not returned

#### Scenario: No series given

- **WHEN** SearchSalesPhases is called with no series
- **THEN** it returns no phases

### Requirement: Values come only from the source pages

Every date, time, classification and name in a discovered phase SHALL come from the searched pages; a value that is not on the pages SHALL be left unknown rather than guessed. A sale whose apply start time cannot be determined SHALL be discarded.

#### Scenario: Lottery with published deadline and result date

- **WHEN** a lottery phase's page publishes the application deadline and the result-announcement date
- **THEN** the discovered phase has both an apply end time and a lottery result time

#### Scenario: Lottery without a published result date

- **WHEN** a lottery phase's page publishes no result-announcement date
- **THEN** the discovered phase's lottery result time is unknown

#### Scenario: No start date on the page

- **WHEN** a page mentions a sale without an application start date
- **THEN** that sale is not returned

#### Scenario: Nothing usable found

- **WHEN** the pages contain no usable sales schedule
- **THEN** SearchSalesPhases returns no phases without an error

### Requirement: Play-guide sales are classified as PLAYGUIDE

A sale conducted through a named play guide (プレイガイド, for example イープラス, ローチケ, チケットぴあ, CN Playguide) SHALL be classified with channel `PLAYGUIDE` and the guide's name as provider name, even when it is a general on-sale. Channel `GENERAL` (一般) SHALL be used only for a general on-sale that names no play guide.

#### Scenario: General on-sale through a play guide

- **WHEN** a general on-sale for a series is sold through イープラス
- **THEN** the discovered phase has channel `PLAYGUIDE` and provider name イープラス

#### Scenario: Direct general on-sale

- **WHEN** a general on-sale is sold directly on the official site with no play guide named
- **THEN** the discovered phase has channel `GENERAL`

### Requirement: Closed sales are excluded

SearchSalesPhases SHALL NOT return a sale whose apply end time is known and before now. A sale whose apply end time is unknown SHALL be returned.

#### Scenario: Sale already closed

- **WHEN** a page lists a presale that closed yesterday
- **THEN** that presale is not returned

#### Scenario: Close not announced

- **WHEN** a page lists a presale with a start date and no end date
- **THEN** that presale is returned

### Requirement: Milestones are in timeline order

In a discovered phase, apply start time, apply end time, lottery result time and payment deadline time SHALL be non-decreasing in that order. A later milestone that is earlier than the milestone before it SHALL be returned as unknown.

#### Scenario: Result before close

- **WHEN** a page yields an apply end time of 10 July and a lottery result time of 5 July
- **THEN** the discovered phase has the apply end time of 10 July and an unknown lottery result time

### Requirement: Search failures

SearchSalesPhases SHALL try a failing search up to 3 times. When the search service stays unreachable or overloaded after the last attempt, it SHALL return no phases without an error. When the search service rejects the request, it SHALL fail with the matching error (InvalidArgument, Unauthenticated, ResourceExhausted, Unavailable or DeadlineExceeded), or Internal for an unexpected failure. A search that finds nothing SHALL return no phases without an error.

#### Scenario: Service down on every attempt

- **WHEN** the search service is unreachable on all 3 attempts
- **THEN** SearchSalesPhases returns no phases without an error

#### Scenario: Request rejected

- **WHEN** the search service rejects the request as unauthenticated
- **THEN** SearchSalesPhases fails with Unauthenticated
