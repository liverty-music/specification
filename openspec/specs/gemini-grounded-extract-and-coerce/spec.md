# gemini-grounded-extract-and-coerce Specification

## Purpose

Defines the two-step Gemini call pipeline that powers `ConcertSearcher.Search` in the backend's `internal/infrastructure/gcp/gemini` package. Step 1 runs a `gemini-3.5-flash` call with `GoogleSearch` and `URLContext` enabled together, fans out into three parallel slices (tours_near, tours_far, standalones), and emits a per-field `<extracted>` XML envelope whose verbatim fields are parsed Go-side. Step 2 runs a `gemini-3.1-flash-lite` call with no tools and `responseJSONSchema` set, receives a JSON list of per-event raw fields, and returns coerced `admin_area` plus RFC 3339 date/time values that are merged back with the Step 1 drafts by `index`. Title / source_url / venue / country never enter Step 2's schema, eliminating LLM-side hallucination paths on those fields. The capability also covers the page-context year-inference rule, the `(local_date, venue, start_time)` Go-side dedup key, per-step tool-set invariants, the per-step `SearchMetadata` fields, and the A/B harness raw-response shape.
## Requirements
### Requirement: Step 1 fills in missing years from page context for partial dates

When the source page emits a date without a year (e.g. `01.16. sat`, `8月7日`), Step 1 SHALL infer the year from page context — the tour title's year range, the page heading, surrounding chronological references — and prefix the verbatim raw value with that year. The emitted `<local_date>` SHALL therefore always carry a 4-digit year as its first token.

#### Scenario: Tour title spans two years and the date is in the second year

- **WHEN** Step 1 reads a page titled "TOUR 2026-2027" with an entry `01.16. sat` after a header listing earlier 2026 dates
- **THEN** the emitted `<local_date>` SHALL be `2027.01.16. sat`

#### Scenario: Tour title spans two years and the date is in the first year

- **WHEN** Step 1 reads the same "TOUR 2026-2027" page with an entry `08.01. sat` near the start of the schedule
- **THEN** the emitted `<local_date>` SHALL be `2026.08.01. sat`

#### Scenario: Source already provides the year

- **WHEN** the source page emits `2026年3月15日(土)` for an event
- **THEN** Step 1 SHALL emit `<local_date>2026年3月15日(土)</local_date>` verbatim with no year prepended

### Requirement: Deduplication keys on (local_date, venue, start_time)

`parseStep2Response` SHALL deduplicate merged results by the triple `(local_date, venue, start_time)` before returning. Two events with identical `(local_date, venue)` but different `start_time` (e.g. 1st-stage 18:00 / 2nd-stage 21:00) SHALL survive as distinct results. Events with identical triples SHALL be folded to a single result, preserving the first occurrence's metadata.

#### Scenario: 1st-stage / 2nd-stage preservation

- **WHEN** the input drafts contain two events at `(2026-08-07, ビルボードライブ大阪, 18:00)` and `(2026-08-07, ビルボードライブ大阪, 21:00)`
- **THEN** the final result SHALL contain both events as distinct entries

#### Scenario: Identical triple → fold

- **WHEN** the input drafts contain two events with identical `(local_date, venue, start_time)` triples
- **THEN** the final result SHALL contain exactly one entry for that triple

#### Scenario: Cross-slice duplicate at the 12-month boundary → fold

- **WHEN** the `tours_near` and `tours_far` slices both extract the same event at the boundary date (`tours_near.to_date` == `tours_far.from_date` == `now + 12mo`), producing two drafts with identical `(local_date, venue, start_time)` triples (e.g. `(2027-05-25, 日本武道館, 18:00:00+09:00)`)
- **THEN** `parseStep2Response` SHALL return exactly one `*entity.ScrapedConcert` for that triple
- **AND** SHALL NOT distinguish the two source slices in the merged output

### Requirement: Step 1 extracts every field in the source page's original language

Step 1 SHALL copy every extracted field — venue in particular — verbatim in the language it is written on the source page, and SHALL NOT translate, romanize, anglicize, or otherwise localize any value, even when the page offers an English or otherwise multilingual view. A Japanese venue name SHALL be emitted in Japanese.

#### Scenario: Multilingual tour page — Japanese venue retained

- **WHEN** Step 1 extracts an event whose venue is printed as `幕張メッセ 9・11ホール` on a page that also offers an English view rendering it "Makuhari Messe Halls 9 & 11"
- **THEN** the emitted `<venue>` SHALL be `幕張メッセ 9・11ホール`
- **AND** it SHALL NOT be romanized or translated to English

#### Scenario: Renamed venue kept verbatim, not semantically translated

- **WHEN** the source prints a venue such as `クロコくんホール（旧 日本ガイシホール）`
- **THEN** the emitted `<venue>` SHALL reproduce that Japanese string verbatim
- **AND** it SHALL NOT be rendered as an English gloss such as "Crocodile Hall"

### Requirement: Step 1 selects the tour-specific page as source_url

For each extracted tour or show, Step 1 SHALL set `source_url` to the artist's page dedicated to THAT specific tour/show — a tour special/feature page or the specific announcement article — in preference to the official-site top page or a generic news-list page, choosing the most detailed tour-specific candidate.

#### Scenario: Tour feature page preferred over the site top

- **WHEN** a tour has a dedicated feature page (e.g. a `/feature/<tour>` page) and the artist also has an official-site top page
- **THEN** `source_url` SHALL be the tour feature page, not the site top page

#### Scenario: No tour-specific page available

- **WHEN** no tour-specific page exists and only a general news-list or top page is available
- **THEN** Step 1 MAY use the most detailed available official page as `source_url`
