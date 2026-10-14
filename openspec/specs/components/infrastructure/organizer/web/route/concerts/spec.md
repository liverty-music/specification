# Concerts

## Purpose

The organizer console's concert list: an Organizer's own concerts and events, with the actions available on each.

## Requirements

### Requirement: An Artist's concerts as a list or a table

The screen SHALL list the concerts that the Artist in its address performs in, cancelled ones last, each with its title, type and performers, its dates (a single date, or the first date followed by 他 N公演 for N more), its venues, the state of its current or next sale, and its publish state as a labelled status. Each concert SHALL be one target that opens its concert page, with no other action inside it. The concerts SHALL be shown as a list while the list area is narrower than 840 px and as a table with the columns 公演名 (title), 日程・会場 (dates and venues), 販売状態 (sale state) and 状態 (publish state) when it is 840 px wide or wider, where the whole row opens the concert, and SHALL change between the two when the area is resized. The screen SHALL offer 公演をつくる (create a concert) as its one floating action, which opens the concert editor with that Artist as the first performer.

#### Scenario: Phone

- **WHEN** an operator opens the concerts of Band A in a 390 px wide window with two concerts
- **THEN** each concert is one list item showing its title, dates, venue, sale state and status, and selecting anywhere on it opens the concert page

#### Scenario: PC

- **WHEN** the same list is opened in a 1280 px wide window
- **THEN** the concerts are rows of a table with the columns 公演名, 日程・会場, 販売状態 and 状態, and selecting a row opens the concert page

#### Scenario: Tour summary

- **WHEN** XX Tour 2026 has events on 3, 10, 17 and 24 November, the first at Zepp Haneda
- **THEN** its dates read 11月3日(火) 他 3公演 and its venue Zepp Haneda 他

#### Scenario: Another Artist's concert

- **WHEN** XX Records represents Band A and Band B and only Band B performs in YY Live
- **THEN** YY Live is not in the concerts of Band A

#### Scenario: Create from an Artist

- **WHEN** an operator presses 公演をつくる on the concerts of Band A
- **THEN** the concert editor opens with Band A as the first performer

### Requirement: Empty and failed lists

When the Artist performs in no concert, the screen SHALL say so and offer 公演をつくる. While the list loads it SHALL show a progress indicator, and when the list cannot be read it SHALL say so and offer 再試行.

#### Scenario: First visit

- **WHEN** an operator opens the concerts of an Artist who performs in none
- **THEN** the screen says there are no concerts yet and offers 公演をつくる

#### Scenario: Load fails

- **WHEN** the list cannot be read
- **THEN** the screen says the concerts could not be loaded and offers 再試行
