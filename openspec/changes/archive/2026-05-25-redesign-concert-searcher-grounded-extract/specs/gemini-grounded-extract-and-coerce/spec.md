## ADDED Requirements

### Requirement: Step 1 fans out into three parallel slices per the default slice configuration

Step 1 SHALL fan out into the slices defined in `defaultStep1Slices`. The default configuration SHALL contain exactly three slices:

| Name | SystemInstruction | PromptTemplate | FromMonthsOffset | ToMonthsOffset |
|------|-------------------|----------------|------------------|------------------|
| `tours_near` | `systemInstructionStep1Tour` | `promptTemplateStep1Tour` | 0 | 12 |
| `tours_far` | `systemInstructionStep1Tour` | `promptTemplateStep1Tour` | 12 | 24 |
| `standalones` | `systemInstructionStep1Standalone` | `promptTemplateStep1Standalone` | 0 | 24 |

Each slice SHALL fire its own Gemini call concurrently with the others using `sync.WaitGroup`-coordinated goroutines. The slice base date SHALL be `time.Now().UTC()`; each slice's `from_date` SHALL be `baseDate.AddDate(0, FromMonthsOffset, 0)` and `to_date` SHALL be `baseDate.AddDate(0, ToMonthsOffset, 0)`, formatted as `2006-01-02`.

#### Scenario: Three goroutines spawned per Search

- **WHEN** `runStep1Grounded` is entered
- **THEN** the function SHALL spawn one goroutine per slice in `defaultStep1Slices`
- **AND** each goroutine SHALL call `runStep1Slice` with that slice and the shared base date
- **AND** the function SHALL wait for all goroutines via `sync.WaitGroup`

#### Scenario: Per-slice date range substitution

- **WHEN** the `tours_near` slice's prompt is constructed and base date is 2026-05-24
- **THEN** the prompt SHALL substitute `from_date = "2026-05-24"`, `to_date = "2027-05-24"`, the artist's name, and the official-site host
- **AND** the `tours_far` slice SHALL substitute `from_date = "2027-05-24"`, `to_date = "2028-05-24"`
- **AND** the `standalones` slice SHALL substitute `from_date = "2026-05-24"`, `to_date = "2028-05-24"`

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

### Requirement: Step 1 instructions follow a five-step workflow in Japanese

Both Step 1 system instructions (`systemInstructionStep1Tour` and `systemInstructionStep1Standalone`) SHALL be written in Japanese and SHALL follow the same five-step numbered workflow:

1. Discover the relevant detail pages for the artist within the date range.
2. Fetch each candidate page and extract the per-field XML.
3. Deduplicate within the slice on the triple `(venue, local_date, start_time)`.
4. MECE check — verify all dates in the range are covered and there is no overlap with other categories.
5. Emit XML only — no prose, no markdown.

The instructions SHALL include the XML output format as a literal example.

#### Scenario: Tour instruction structure

- **WHEN** `systemInstructionStep1Tour` is loaded
- **THEN** the instruction text SHALL contain a numbered list with five entries
- **AND** the instruction text SHALL include the XML example with `<extracted>`, `<tour>`, `<title>`, `<source_url>`, `<event>` elements

#### Scenario: Standalone instruction structure

- **WHEN** `systemInstructionStep1Standalone` is loaded
- **THEN** the instruction text SHALL contain a numbered list with five entries
- **AND** the instruction text SHALL include the XML example with `<extracted>`, `<standalone>`, `<title>`, `<source_url>`, `<event>` elements

### Requirement: Step 1 prompt template uses four positional placeholders

Both Step 1 prompt templates (`promptTemplateStep1Tour` and `promptTemplateStep1Standalone`) SHALL accept exactly four positional placeholders in this order: `from_date`, `to_date`, artist name, official-site host. Each call SHALL format the template via `fmt.Sprintf`. The tour template SHALL request tour-only output and SHALL exclude festivals and standalones. The standalone template SHALL request standalone-only output and SHALL exclude festivals and multi-date tours.

#### Scenario: Tour prompt formatting

- **WHEN** `promptTemplateStep1Tour` is formatted with `("2026-05-24", "2027-05-24", "UVERworld", "www.uverworld.jp")`
- **THEN** the result SHALL contain `2026-05-24`, `2027-05-24`, `UVERworld`, and `www.uverworld.jp` literally
- **AND** the result SHALL instruct the model to extract tours and exclude festivals and standalones

#### Scenario: Standalone prompt formatting

- **WHEN** `promptTemplateStep1Standalone` is formatted with the same four arguments
- **THEN** the result SHALL instruct the model to extract standalone shows (including ファンクラブ限定ライブ and 2–4-act 対バン) and exclude festivals and tours

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
