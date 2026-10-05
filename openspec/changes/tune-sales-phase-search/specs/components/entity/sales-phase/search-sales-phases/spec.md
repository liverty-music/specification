# Spec Delta

## ADDED Requirements

### Requirement: Only sales that have not opened are returned

SearchSalesPhases SHALL return only sales whose apply start time is after the current time, including lotteries and first-come sales, presales and general on-sales, and every later round (2次, 3次, …) of a series that has not opened yet. A sale that has already opened, whether still open or closed, SHALL NOT be returned. Ticket trades and resales between ticket holders (公式トレード, リセール) SHALL NOT be returned.

#### Scenario: Two rounds announced ahead

- **WHEN** a fan-club page announces a first round opening tomorrow and a second round opening next month
- **THEN** both rounds are returned as two discovered phases

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
- **THEN** the discovered phase opens at 1 November 13:00 Japan time

#### Scenario: Year omitted

- **WHEN** the series' events run from February to March 2027 and the page states a sale opening on 10 November without a year
- **THEN** the discovered phase opens on 10 November 2026

### Requirement: Required values come from the source pages

Every value in a discovered phase SHALL come from the searched pages; a value SHALL never be guessed. A sale SHALL be returned only when the pages state its method and its apply start time, and for a lottery also its apply end time. Otherwise the sale SHALL be discarded. A first-come sale whose pages state no end SHALL be returned without an apply end time. A lottery result time SHALL be returned when the pages state it and left unknown otherwise.

#### Scenario: Lottery with a published result date

- **WHEN** a lottery's page states its application period and its result-announcement date
- **THEN** the discovered phase has an apply start time, an apply end time and a lottery result time

#### Scenario: Lottery without a published result date

- **WHEN** a lottery's page states its application period and no result-announcement date
- **THEN** the discovered phase has no lottery result time

#### Scenario: First-come sale until sold out

- **WHEN** a page announces a fan-club first-come sale that opens tomorrow at 18:30 and ends when tickets run out
- **THEN** the discovered phase has method `FIRST_COME`, an apply start time and no apply end time

#### Scenario: Lottery without a stated close

- **WHEN** a page announces a lottery with a start date and no end date
- **THEN** that sale is not returned

#### Scenario: Method not stated

- **WHEN** a page announces a sale without saying whether it is a lottery or first come
- **THEN** that sale is not returned

#### Scenario: Nothing usable found

- **WHEN** the pages contain no sale that has not opened
- **THEN** SearchSalesPhases returns no phases without an error

### Requirement: Inconsistent sales are discarded

A sale SHALL be discarded when its milestones break the Sales Phase rules, or when its apply start time is after the last day of its series' event period.

#### Scenario: Close before open

- **WHEN** a page yields an apply start time of 10 July and an apply end time of 5 July
- **THEN** that sale is not returned

#### Scenario: Opening after the last show

- **WHEN** a series' last event is on 20 December and a sale is read as opening on 10 January
- **THEN** that sale is not returned

### Requirement: A failed search fails

SearchSalesPhases SHALL call the search service once per search. SearchSalesPhases SHALL fail with an error, and return no phases, in these cases:

- The service is unreachable or overloaded: Unavailable.
- The service rejects the request: the matching error (InvalidArgument, Unauthenticated, ResourceExhausted including a spend cap, or DeadlineExceeded).
- The service returns no result, or a result that cannot be read: Internal.

A readable result that lists no sale SHALL return no phases without an error.

#### Scenario: Spend cap reached

- **WHEN** the search service rejects the request because the monthly spend cap is reached
- **THEN** SearchSalesPhases fails with ResourceExhausted

#### Scenario: No result

- **WHEN** the search service answers without a result
- **THEN** SearchSalesPhases fails with Internal

#### Scenario: Service unreachable

- **WHEN** the search service is unreachable
- **THEN** SearchSalesPhases fails with Unavailable

## MODIFIED Requirements

### Requirement: One search covers all of an artist's upcoming series

SearchSalesPhases SHALL take the artist, the artist's official site, and the series to search. Each series SHALL be given with its title and its event period (the dates of its first and last events). SearchSalesPhases SHALL return discovered phases, each attributed to exactly one of the given series. A sale that cannot be attributed to one of the given series SHALL be discarded. The search SHALL NOT resolve which events of a series a phase covers. When no series is given, SearchSalesPhases SHALL return no phases without searching.

#### Scenario: Artist with two tours

- **WHEN** SearchSalesPhases runs for an artist with two series and the pages announce an upcoming presale for one of them
- **THEN** it returns one discovered phase, attributed to that series

#### Scenario: Unattributable sale

- **WHEN** the pages announce an upcoming sale that matches none of the given series
- **THEN** that sale is not returned

#### Scenario: No series given

- **WHEN** SearchSalesPhases is called with no series
- **THEN** it returns no phases

## REMOVED Requirements

### Requirement: Play-guide sales are classified as PLAYGUIDE

**Reason**: Channel and provider name are removed from the Sales Phase.
**Migration**: None; no notification reads them.

### Requirement: Closed sales are excluded

**Reason**: Replaced by "Only sales that have not opened are returned", which excludes closed sales and also those already open.
**Migration**: None.

### Requirement: Values come only from the source pages

**Reason**: A sale is now returned only with every required value stated on the pages.
**Migration**: Replaced by "Required values come from the source pages".

### Requirement: Milestones are in timeline order

**Reason**: An inconsistent sale is now discarded instead of having later milestones cleared.
**Migration**: Replaced by "Inconsistent sales are discarded".

### Requirement: Search failures

**Reason**: A failure no longer degrades to no phases, so the next daily run searches again.
**Migration**: Replaced by "A failed search fails".
