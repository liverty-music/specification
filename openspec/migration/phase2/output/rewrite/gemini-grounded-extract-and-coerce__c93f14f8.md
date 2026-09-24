<!-- spec: gemini-grounded-extract-and-coerce | target: components/usecase/concert/search-new-concerts | flags: CLASSNAME | new_name: Discovered concerts deduplicated by date, venue, and start time -->

### Requirement: Deduplication keys on (local_date, venue, start_time)

Discovered concerts SHALL be deduplicated by the triple `(local_date, venue, start_time)` before being returned. Two events with identical `(local_date, venue)` but different `start_time` (e.g. 1st-stage 18:00 / 2nd-stage 21:00) SHALL survive as distinct results. Events with identical triples SHALL be folded to a single result, preserving the first occurrence's metadata.

#### Scenario: 1st-stage / 2nd-stage preservation

- **WHEN** the input drafts contain two events at `(2026-08-07, ビルボードライブ大阪, 18:00)` and `(2026-08-07, ビルボードライブ大阪, 21:00)`
- **THEN** the final result SHALL contain both events as distinct entries

#### Scenario: Identical triple → fold

- **WHEN** the input drafts contain two events with identical `(local_date, venue, start_time)` triples
- **THEN** the final result SHALL contain exactly one entry for that triple

#### Scenario: Cross-slice duplicate at the 12-month boundary → fold

- **WHEN** two overlapping search windows (a near-term window and a far-term window) both extract the same event at their shared boundary date (i.e., the near window's end date equals the far window's start date, at now + 12 months), producing two drafts with identical `(local_date, venue, start_time)` triples (e.g. `(2027-05-25, 日本武道館, 18:00:00+09:00)`)
- **THEN** the deduplication SHALL return exactly one discovered concert for that triple
- **AND** SHALL NOT distinguish which of the two search windows the result came from in the merged output
