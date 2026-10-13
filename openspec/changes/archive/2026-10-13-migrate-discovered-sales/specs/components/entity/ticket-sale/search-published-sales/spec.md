# Spec Delta

## Purpose

SearchPublishedSales looks up, in one search per artist, the ticket sales that have not opened yet for the given series of the artist. It reads the artist's official site and official ticket pages and returns each sale as a discovered sale attributed to one of those series. Extraction is best-effort: its results are verified by an integration test against real pages, not guaranteed per page.

## ADDED Requirements

### Requirement: One search covers all of an artist's upcoming series

SearchPublishedSales SHALL take the artist, the artist's official site, and the series to search. Each series SHALL be given with its title and its event period (the dates of its first and last events). SearchPublishedSales SHALL return discovered sales, each attributed to exactly one of the given series. A sale that cannot be attributed to one of the given series SHALL be discarded. The search SHALL NOT resolve which events of a series a sale covers. When no series is given, SearchPublishedSales SHALL return no sales without searching.

#### Scenario: Artist with two tours
- **WHEN** SearchPublishedSales runs for an artist with two series and the pages announce an upcoming presale for one of them
- **THEN** it returns one discovered sale, attributed to that series

#### Scenario: Unattributable sale
- **WHEN** the pages announce an upcoming sale that matches none of the given series
- **THEN** that sale is not returned

#### Scenario: No series given
- **WHEN** SearchPublishedSales is called with no series
- **THEN** it returns no sales

### Requirement: Only sales that have not opened are returned

SearchPublishedSales SHALL return only sales whose start time is after the current time, including lotteries and first-come sales, presales and general on-sales, and every later round (2次, 3次, …) of a series that has not opened yet. A sale that has already opened, whether still open or closed, SHALL NOT be returned. Ticket trades and resales between fans (公式トレード, リセール) SHALL NOT be returned.

#### Scenario: Two rounds announced ahead
- **WHEN** a fan-club page announces a first round opening tomorrow and a second round opening next month
- **THEN** both rounds are returned as two discovered sales

#### Scenario: Sale already open
- **WHEN** a page lists a presale that opened yesterday and closes next week
- **THEN** that presale is not returned

#### Scenario: Official ticket trade
- **WHEN** a page lists an official ticket trade for the series that opens tomorrow
- **THEN** the trade is not returned

### Requirement: Times are read in the time zone of the page

Every milestone time SHALL be read in the time zone the source page uses and returned as an absolute instant. When a page omits the year of a date, the year SHALL be the one that places the date before the end of the series' event period.

#### Scenario: Sale abroad
- **WHEN** a page for a Taipei show states that a sale opens on 1 November at 12:00 local time
- **THEN** the discovered sale opens at 1 November 13:00 Japan time

#### Scenario: Year omitted
- **WHEN** the series' events run from February to March 2027 and the page states a sale opening on 10 November without a year
- **THEN** the discovered sale opens on 10 November 2026

### Requirement: Required values come from the source pages

Every value in a discovered sale SHALL come from the searched pages; a value SHALL never be guessed. A sale SHALL be returned only when the pages state its method and its start time, and for a lottery also its end time. Otherwise the sale SHALL be discarded. A first-come sale whose pages state no end SHALL be returned without an end time. A lottery result time SHALL be returned when the pages state it and left unknown otherwise.

#### Scenario: Lottery with a published result date
- **WHEN** a lottery's page states its application period and its result-announcement date
- **THEN** the discovered sale has a start time, an end time and a lottery result time

#### Scenario: Lottery without a published result date
- **WHEN** a lottery's page states its application period and no result-announcement date
- **THEN** the discovered sale has no lottery result time

#### Scenario: First-come sale until sold out
- **WHEN** a page announces a fan-club first-come sale that opens tomorrow at 18:30 and ends when tickets run out
- **THEN** the discovered sale has method FirstCome, a start time and no end time

#### Scenario: Lottery without a stated close
- **WHEN** a page announces a lottery with a start date and no end date
- **THEN** that sale is not returned

#### Scenario: Method not stated
- **WHEN** a page announces a sale without saying whether it is a lottery or first come
- **THEN** that sale is not returned

#### Scenario: Nothing usable found
- **WHEN** the pages contain no sale that has not opened
- **THEN** SearchPublishedSales returns no sales without an error

### Requirement: Inconsistent sales are discarded

A sale SHALL be discarded when its times break the TicketSale rules for a discovered sale, or when its start time is after the last day of its series' event period.

#### Scenario: Close before open
- **WHEN** a page yields a start time of 10 July and an end time of 5 July
- **THEN** that sale is not returned

#### Scenario: Opening after the last show
- **WHEN** a series' last event is on 20 December and a sale is read as opening on 10 January
- **THEN** that sale is not returned

### Requirement: A failed search fails

SearchPublishedSales SHALL call the search service once per search, and a second time only when the service rejects the first request as invalid: that second request SHALL be the same request without the optional report of the search service's own tool calls. SearchPublishedSales SHALL fail with an error, and return no sales, in these cases:

- The service is unreachable or overloaded: Unavailable.
- The service rejects the request: the matching error (InvalidArgument when the request without the tool-call report is rejected as invalid too, Unauthenticated, ResourceExhausted including a spend cap, or DeadlineExceeded).
- The service returns no result, or a result that cannot be read: Internal.

A readable result that lists no sale SHALL return no sales without an error.

#### Scenario: Spend cap reached
- **WHEN** the search service rejects the request because the monthly spend cap is reached
- **THEN** SearchPublishedSales fails with ResourceExhausted

#### Scenario: No result
- **WHEN** the search service answers without a result
- **THEN** SearchPublishedSales fails with Internal

#### Scenario: Service unreachable
- **WHEN** the search service is unreachable
- **THEN** SearchPublishedSales fails with Unavailable

#### Scenario: Invalid request recovered without the tool report
- **WHEN** the search service rejects the request as invalid and accepts it without the tool-call report
- **THEN** SearchPublishedSales returns the sales of the second request

#### Scenario: Invalid request rejected twice
- **WHEN** the search service rejects the request as invalid with and without the tool-call report
- **THEN** SearchPublishedSales fails with InvalidArgument after those two requests
