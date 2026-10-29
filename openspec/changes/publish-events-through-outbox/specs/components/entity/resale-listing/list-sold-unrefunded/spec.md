## MODIFIED Requirements

### Requirement: Sold listings left to finish

ListSoldUnrefunded SHALL return every Sold ResaleListing that has no refund time, oldest sold time first, and an empty list when there are none.

#### Scenario: Just sold
- **WHEN** a listing became Sold a moment ago
- **THEN** it is returned

#### Scenario: Refunded, email not sent
- **WHEN** a Sold listing has a refund time and no sold email send time
- **THEN** it is not returned

#### Scenario: Finished
- **WHEN** a Sold listing has a refund time and a sold email send time
- **THEN** it is not returned

#### Scenario: Listed listing
- **WHEN** a listing is still Listed
- **THEN** it is not returned
