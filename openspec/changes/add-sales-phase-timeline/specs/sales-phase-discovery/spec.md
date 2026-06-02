## ADDED Requirements

### Requirement: Dedicated Sales-Phase Searcher

The system SHALL provide a sales-phase searcher that is separate from the concert searcher, because the concert searcher's grounding (the artist's official site) does not contain ticket sales schedules. The sales-phase searcher SHALL take an artist name and a series title as input and extract that series' sales phases.

#### Scenario: Search sales phases for a series

- **WHEN** the searcher is invoked with an artist name and a series title
- **THEN** it SHALL issue a Gemini call grounded to find that series' ticket sales information
- **AND** it SHALL return the extracted sales phases for that series

#### Scenario: One call per series

- **WHEN** discovery processes multiple series
- **THEN** the searcher SHALL issue one Gemini call per series, looping over the series

### Requirement: Verbatim Extraction Discipline

The searcher SHALL follow a two-step discipline to suppress hallucinated dates: a grounded step that extracts schedule values verbatim and retains the source URL, and a coercion step that only normalizes the extracted values into canonical date/time formats.

#### Scenario: Verbatim extract then coerce

- **WHEN** the searcher extracts a sales phase
- **THEN** schedule values SHALL be extracted verbatim from grounded content in the first step
- **AND** a source URL SHALL be retained for the extracted phase
- **AND** the second step SHALL only coerce those values into canonical formats, not invent new ones

#### Scenario: No actionable data found

- **WHEN** the grounding contains no usable sales-schedule information for the series
- **THEN** the searcher SHALL produce no sales phase for that series

### Requirement: Scheduled Sales-Phase Discovery Job

The system SHALL run a scheduled job that discovers sales phases for the upcoming series of followed artists and upserts them into storage.

#### Scenario: Scheduled execution

- **WHEN** the discovery job runs on its schedule
- **THEN** it SHALL enumerate the series of followed artists that have upcoming events
- **AND** invoke the sales-phase searcher for each such series
- **AND** upsert the resulting sales phases

#### Scenario: Idempotent re-run

- **WHEN** the discovery job runs again over the same series
- **THEN** previously discovered phases SHALL converge to the same rows via the upsert key
- **AND** no duplicate sales phases SHALL be created
