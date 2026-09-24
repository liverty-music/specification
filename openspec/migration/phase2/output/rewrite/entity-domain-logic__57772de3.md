<!-- spec: entity-domain-logic | target: components/entity/concert | flags: CLASSNAME | new_name: Discovered-concert deduplication by date -->

### Requirement: Discovered-concert deduplication by date

Newly discovered (scraped) concerts SHALL be deduplicated against a set of existing concerts using date-only comparison: a discovered concert is considered a duplicate if its local event date matches the local event date of an existing concert, or the local event date of an earlier discovered concert already kept from the same batch. Discovered concerts SHALL be evaluated in their original order, and only concerts whose date does not conflict SHALL be kept, in that same order. This deduplication SHALL apply both across batches (against previously known concerts) and within a single batch (concerts discovered together).

#### Scenario: Empty scraped list

- **WHEN** the discovered-concerts list is empty and the existing concerts are any value
- **THEN** no concerts SHALL be kept

#### Scenario: No existing concerts

- **WHEN** there are no existing concerts and the discovered concerts have different dates
- **THEN** all discovered concerts SHALL be kept

#### Scenario: All scraped concerts conflict with existing

- **WHEN** every discovered concert's date matches an existing concert's date
- **THEN** no discovered concerts SHALL be kept

#### Scenario: Partial overlap with existing

- **WHEN** 3 concerts are discovered, 1 conflicts with an existing concert and 2 do not
- **THEN** the 2 non-conflicting concerts SHALL be kept, in their original order

#### Scenario: Within-batch duplicate on same date

- **WHEN** 2 discovered concerts share the same date and no existing concert has that date
- **THEN** only the first of the two SHALL be kept (within-batch dedup)

#### Scenario: Within-batch duplicate conflicts with existing

- **WHEN** 2 discovered concerts share the same date, and that date also matches an existing concert
- **THEN** neither discovered concert SHALL be kept

#### Scenario: Preserves original order

- **WHEN** discovered concerts have dates in the order [Mar 15, Mar 17, Mar 16] and none conflict
- **THEN** they SHALL be kept in that same order [Mar 15, Mar 17, Mar 16]

#### Scenario: Nil existing concerts

- **WHEN** there is no record of existing concerts and concerts have been discovered
- **THEN** all discovered concerts SHALL be kept (there is nothing to conflict with)
