## ADDED Requirements

### Requirement: Dedup Tolerates Venue Name Drift

The concert dedup natural key SHALL compare its `listed_venue_name` component (as defined by
the "Concert Deduplication Natural Key" requirement) on a normalized form rather than as a raw
string, so that the same physical venue reported
under different surface strings across discovery runs (for example
`フェスティバルホール` vs `大阪・フェスティバルホール`, or `新潟テルサ` vs
`新潟・新潟テルサ`) is recognised as the same venue and does not defeat deduplication
against existing events or pending staged rows. Normalization SHALL at minimum fold
whitespace and full/half-width variants and strip leading administrative-area or
city-prefix decorations (e.g. `〈admin_area〉・`, `〈city〉公演 ＠`). The `(local_event_date,
start_at)` components of the natural key SHALL be unchanged. The event natural key
`(venue_id, local_event_date, start_at)` SHALL remain the final database-level safety net
when normalization is insufficient.

#### Scenario: Prefixed venue name matches the same unprefixed venue

- **WHEN** a scraped concert has `listed_venue_name = "フェスティバルホール"`
- **AND** an existing event at the same `local_event_date` and `start_at` was stored with
  `listed_venue_name = "大阪・フェスティバルホール"`
- **THEN** the scraped concert SHALL be treated as a duplicate after name normalization
- **AND** SHALL NOT be published in the `concert.discovered.v1` event

#### Scenario: Normalization does not merge genuinely different venues

- **WHEN** two scraped concerts share `local_event_date` and `start_at`
- **AND** their venue names normalize to different values
- **THEN** they SHALL remain distinct events
- **AND** both SHALL be eligible for publication

#### Scenario: Drifted name recognised against a pending staged row

- **WHEN** a scraped concert normalizes to the same venue, date, and start as a concert
  already present in the approval queue in `pending` state
- **THEN** the scraped concert SHALL be treated as already-known
- **AND** SHALL NOT be re-staged
