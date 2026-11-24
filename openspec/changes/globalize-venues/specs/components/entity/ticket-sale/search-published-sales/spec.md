## MODIFIED Requirements

### Requirement: One search covers all of an artist's upcoming series

SearchPublishedSales SHALL take the artist, the artist's official site, and the series to search. Each series SHALL be given with its title, its event period (the dates of its first and last events) and, when the Venues of its upcoming events all have the same time zone, that time zone. SearchPublishedSales SHALL return discovered sales, each attributed to exactly one of the given series. A sale that cannot be attributed to one of the given series SHALL be discarded. The search SHALL NOT resolve which events of a series a sale covers. When no series is given, SearchPublishedSales SHALL return no sales without searching.

#### Scenario: Artist with two tours
- **WHEN** SearchPublishedSales runs for an artist with two series and the pages announce an upcoming presale for one of them
- **THEN** it returns one discovered sale, attributed to that series

#### Scenario: Unattributable sale
- **WHEN** the pages announce an upcoming sale that matches none of the given series
- **THEN** that sale is not returned

#### Scenario: No series given
- **WHEN** SearchPublishedSales is called with no series
- **THEN** it returns no sales

### Requirement: Times are read in the time zone of the page

Every milestone time SHALL be returned as the local date-time the source page states, with the IANA time zone the page states or implies, such as Asia/Taipei for a time given as Taipei time; it SHALL NOT be converted to another zone. When the page implies no time zone, the sale SHALL take the time zone given with its series; when the series was given without one, the sale SHALL be discarded. Whether a sale has opened SHALL be judged by the instant of its start time in its time zone. When a page omits the year of a date, the year SHALL be the one that places the date before the end of the series' event period.

#### Scenario: Sale abroad
- **WHEN** a page for a Taipei show states that a sale opens on 1 November at 12:00 local time
- **THEN** the discovered sale opens on 1 November 12:00 in the time zone Asia/Taipei

#### Scenario: Zone taken from the series
- **WHEN** a page states that a sale opens on 1 November at 12:00 and implies no time zone, and the series was given with the time zone Europe/London
- **THEN** the discovered sale opens on 1 November 12:00 in the time zone Europe/London

#### Scenario: No zone anywhere
- **WHEN** a page states a sale's times and implies no time zone, and the series, with events in Asia/Tokyo and Asia/Seoul, was given without a time zone
- **THEN** that sale is not returned

#### Scenario: Year omitted
- **WHEN** the series' events run from February to March 2027 and the page states a sale opening on 10 November without a year
- **THEN** the discovered sale opens on 10 November 2026

### Requirement: Inconsistent sales are discarded

A sale SHALL be discarded when its times break the TicketSale rules for a discovered sale, including a start or end time that does not exist in the sale's time zone, or when its start date is after the last day of its series' event period.

#### Scenario: Close before open
- **WHEN** a page yields a start time of 10 July and an end time of 5 July
- **THEN** that sale is not returned

#### Scenario: Opening after the last show
- **WHEN** a series' last event is on 20 December and a sale is read as opening on 10 January
- **THEN** that sale is not returned

#### Scenario: Time skipped by the clock change
- **WHEN** a page yields a sale opening on 2027-03-14 02:30 in the time zone America/New_York, a time the clocks skip that night
- **THEN** that sale is not returned

### Requirement: A lottery's result date is returned when the pages state it

For a discovered Lottery sale, SearchPublishedSales SHALL return the result date when the searched pages state the day the lottery's results are announced, as the calendar day the page states, without converting it to another zone. It SHALL return no result date when the pages do not state that day, for a first-come sale, and when the stated day is before the day of the sale's end time; in each of these cases the sale itself SHALL still be returned.

#### Scenario: Lottery page states the result day

- **WHEN** a lottery's page states its application period and 「当落発表：11月3日(月)15:00」
- **THEN** the discovered sale has the result date 3 November

#### Scenario: Result day abroad

- **WHEN** a page for a London show states that a lottery's results are announced on 3 November at 20:00 London time, which is 4 November in Japan time
- **THEN** the discovered sale has the result date 3 November

#### Scenario: Result announced over several days

- **WHEN** a lottery's page states 「当落発表：11月3日(月)〜11月5日(水)」
- **THEN** the discovered sale has the result date 3 November

#### Scenario: No result day on the page

- **WHEN** a lottery's page states its application period and no result day
- **THEN** the sale is returned without a result date

#### Scenario: Result day before the close

- **WHEN** a page yields a lottery closing on 22 October and a result day of 20 October
- **THEN** the sale is returned without a result date
