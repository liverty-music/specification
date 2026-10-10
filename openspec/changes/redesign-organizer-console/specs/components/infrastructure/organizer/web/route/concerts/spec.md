# Spec Delta

## ADDED Requirements

### Requirement: The Organizer's concerts as cards or a table

The screen SHALL list the Organizer's concerts, cancelled ones last, each with its title, type and performers, its dates (a single date, or the first date followed by 他 N公演 for N more), its venues, the state of its current or next sale, and its publish state as a labelled badge; each concert SHALL open its concert page. The list SHALL be shown as cards while the list area is narrower than 840 px and as a table with the columns 公演名 (title), 日程・会場 (dates and venues), 販売状態 (sale state) and 状態 (publish state) when it is 840 px wide or wider, and SHALL change between the two when the area is resized. The screen SHALL offer 公演をつくる (create a concert), which opens the concert editor.

#### Scenario: Phone

- **WHEN** an operator opens Concerts in a 390 px wide window with two concerts
- **THEN** each concert is a card showing its title, dates, venue, sale state and badge

#### Scenario: PC

- **WHEN** the same list is opened in a 1280 px wide window
- **THEN** the concerts are rows of a table with the columns 公演名, 日程・会場, 販売状態 and 状態

#### Scenario: Tour summary

- **WHEN** XX Tour 2026 has events on 3, 10, 17 and 24 November, the first at Zepp Haneda
- **THEN** its dates read 11月3日(火) 他 3公演 and its venue Zepp Haneda 他

### Requirement: Empty and failed lists

When the Organizer has no concert, the screen SHALL say so and offer 公演をつくる. While the list loads it SHALL show a progress indicator, and when the list cannot be read it SHALL say so and offer 再試行.

#### Scenario: First visit

- **WHEN** an Organizer without concerts opens Concerts
- **THEN** the screen says there are no concerts yet and offers 公演をつくる

#### Scenario: Load fails

- **WHEN** the list cannot be read
- **THEN** the screen says the concerts could not be loaded and offers 再試行

## REMOVED Requirements

### Requirement: Organizer console entry point to lottery configuration

**Reason**: Sales are now reached per event: the concert page lists its events and each event page has a Sales tab with the lottery entry. The concerts list no longer carries per-event actions.
**Migration**: The entry point is specified in `components/infrastructure/organizer/web/route/event` ("The Sales tab explains a missing prerequisite", "Start a lottery from the Sales tab"); a draft event still cannot start a sale.
