## ADDED Requirements

### Requirement: A lottery's result date is returned when the pages state it

For a discovered Lottery sale, SearchPublishedSales SHALL return the result date when the searched pages state the day the lottery's results are announced, read in the time zone of the page. It SHALL return no result date when the pages do not state that day, for a first-come sale, and when the stated day is before the day of the sale's end time; in each of these cases the sale itself SHALL still be returned.

#### Scenario: Lottery page states the result day

- **WHEN** a lottery's page states its application period and 「当落発表：11月3日(月)15:00」
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
