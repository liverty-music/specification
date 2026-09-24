<!-- spec: entity-domain-logic | target: components/entity/concert | flags: CLASSNAME | new_name: Discovered-concert JSON payload encoding -->

### Requirement: Discovered-concert JSON payload encoding

The discovered-concert entity SHALL have JSON tags on all fields to support serialization as an event payload.

Field-to-JSON-tag mapping:
- `Title` → `"title"`
- `ListedVenueName` → `"listed_venue_name"`
- `AdminArea` → `"admin_area,omitempty"`
- `LocalDate` → `"local_date"`
- `StartTime` → `"start_time,omitempty"`
- `OpenTime` → `"open_time,omitempty"`
- `SourceURL` → `"source_url"`

#### Scenario: Marshal omits nil optional fields

- **WHEN** a discovered-concert entity with `AdminArea=nil`, `StartTime=nil`, `OpenTime=nil` is marshaled to JSON
- **THEN** the JSON output does not contain `"admin_area"`, `"start_time"`, or `"open_time"` keys

#### Scenario: Marshal includes all non-nil fields

- **WHEN** a discovered-concert entity with all fields set is marshaled to JSON
- **THEN** all 7 fields appear in the JSON output with correct key names
