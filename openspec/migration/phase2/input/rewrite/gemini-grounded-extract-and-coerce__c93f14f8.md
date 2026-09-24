<!-- spec: gemini-grounded-extract-and-coerce | target: components/usecase/concert/search-new-concerts | flags: CLASSNAME | new_name: Discovered concerts deduplicated by date, venue, and start time -->

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
