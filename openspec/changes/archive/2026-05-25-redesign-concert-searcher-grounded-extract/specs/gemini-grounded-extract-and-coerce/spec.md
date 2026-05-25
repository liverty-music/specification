## ADDED Requirements

### Requirement: ConcertSearcher executes a two-step Gemini call sequence per Search invocation

The `ConcertSearcher.Search` method SHALL execute exactly two Gemini API calls per invocation under the `gemini-grounded-extract-and-coerce` capability: Step 1 (grounded extract) and Step 2 (JSON coerce). Step 1 MAY fan out into multiple parallel sub-calls (slices); regardless of slice count, Step 1 SHALL complete before Step 2 starts. The flattened result of Step 2 SHALL be merged Go-side with the Step 1 verbatim drafts and returned to the caller as `[]*entity.ScrapedConcert`, preserving the public signature.

#### Scenario: Happy path — Step 1 and Step 2 both succeed

- **WHEN** `Search` is called with a non-nil `OfficialSite`
- **THEN** the searcher SHALL fan out Step 1 into the slices defined by `defaultStep1Slices`
- **AND** wait for all slices to complete
- **AND** merge each slice's `<extracted>` envelope into a single envelope via `mergeAndDedupEnvelopes`
- **AND** parse the merged envelope into `[]EventDraft` via `parseStep1Envelope`
- **AND** issue Step 2 with the per-event JSON payload derived from the drafts
- **AND** merge Step 2's coerced output back with the drafts by `index`
- **AND** return the deduplicated `[]*entity.ScrapedConcert` to the caller

#### Scenario: Step 1 permanent error from any slice → Search returns the error

- **WHEN** any Step 1 slice returns a permanent error (4xx, invalid argument, quota exhausted) after the retry policy
- **THEN** Step 2 SHALL NOT run
- **AND** the first permanent error encountered SHALL be wrapped per `toAppErr` semantics and returned

#### Scenario: Step 1 transient retry exhaustion on one slice → other slices' results proceed to Step 2

- **WHEN** one Step 1 slice exhausts its retries with a transient error
- **AND** at least one other slice succeeds
- **THEN** the failed slice's envelope SHALL be treated as empty
- **AND** the merged envelope SHALL still flow to Step 2 with the succeeding slices' content

#### Scenario: Step 2 permanent error → Search returns the error

- **WHEN** Step 2 returns a permanent error
- **THEN** the wrapped error SHALL propagate to the caller
- **AND** no partial result SHALL be returned

#### Scenario: Step 2 invalid JSON → permanent error propagates

- **WHEN** Step 2's response is not valid JSON or does not satisfy `responseJSONSchema`
- **THEN** `SearchMetadata.InvalidJSON` SHALL be set to true
- **AND** the wrapped `errInvalidJSON` SHALL propagate to the caller

### Requirement: Step 1 fans out into three parallel slices per the default slice configuration

Step 1 SHALL fan out into the slices defined in `defaultStep1Slices`. The default configuration SHALL contain exactly three slices:

| Name | SystemInstruction | PromptTemplate | FromMonthsOffset | ToMonthsOffset |
|------|-------------------|----------------|------------------|----------------|
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

### Requirement: Step 1 tools MUST be {GoogleSearch, URLContext} together; no schema

Step 1's `GenerateContentConfig.Tools` SHALL contain exactly two tool entries — one with `GoogleSearch` populated and one with `URLContext` populated. No other tool SHALL be present. `GenerateContentConfig.ResponseJsonSchema` SHALL be nil and `ResponseMIMEType` SHALL NOT be set to `application/json`. The `assertStepInvariants("step1_grounded", cfg)` guard SHALL enforce this contract and return an internal error before the API call is issued if any invariant is violated.

#### Scenario: Step 1 request shape

- **WHEN** Step 1's request is constructed
- **THEN** `cfg.Tools` SHALL contain exactly one `GoogleSearch` element and exactly one `URLContext` element
- **AND** `cfg.ResponseJsonSchema` SHALL be nil

#### Scenario: Invariant guard rejects misconfigured Step 1

- **WHEN** `assertStepInvariants("step1_grounded", cfg)` is called with a tool set other than `{GoogleSearch, URLContext}`
- **THEN** the helper SHALL return an internal error
- **AND** the caller SHALL NOT issue the Gemini API call

### Requirement: Step 1 emits a per-field XML envelope with `<tour>` and `<standalone>` blocks

Step 1 SHALL emit its response as a single `<extracted>...</extracted>` XML envelope. Inside the envelope, each multi-date tour SHALL be expressed as one `<tour>` block containing `<title>`, `<source_url>`, and one or more `<event>` children. Each one-off / single-date concert SHALL be expressed as one `<standalone>` block containing `<title>`, `<source_url>`, and exactly one `<event>` child.

Each `<event>` block SHALL contain `<venue>`, `<country>`, `<local_date>`, `<open_time>`, and `<start_time>` children, in any order. Empty values SHALL be emitted as empty elements (`<open_time></open_time>`), never as `null` and never omitted from the block.

#### Scenario: Tour with multiple dates

- **WHEN** Step 1 finds a tour with three dates announced
- **THEN** the envelope SHALL contain one `<tour>` block
- **AND** the block SHALL have one `<title>`, one `<source_url>`, and three `<event>` children

#### Scenario: One-off concert

- **WHEN** Step 1 finds a single-date standalone show
- **THEN** the envelope SHALL contain one `<standalone>` block
- **AND** the block SHALL have one `<title>`, one `<source_url>`, and exactly one `<event>` child

#### Scenario: Missing field — empty element

- **WHEN** the source page does not state `open_time` for an event
- **THEN** the `<event>` block SHALL still contain `<open_time></open_time>` (an empty element)
- **AND** the element SHALL NOT be omitted

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

### Requirement: Go-side verbatim parse extracts title, source_url, venue, country, and raw date/time strings

The function `parseStep1Envelope` SHALL unmarshal the merged Step 1 envelope into a flat `[]EventDraft`. For each `<tour>` block, one draft SHALL be emitted per child `<event>`, with `Title` taken from `<title>` and `SourceURL` taken from `<source_url>`. For each `<standalone>` block, exactly one draft SHALL be emitted, with `Title` and `SourceURL` taken from the block's own `<title>` and `<source_url>` children. Each draft SHALL carry the verbatim `<venue>`, `<country>`, `<local_date>`, `<open_time>`, and `<start_time>` text trimmed of surrounding whitespace.

On unparseable input (non-XML body, malformed structure), `parseStep1Envelope` SHALL return an empty slice without an error so Step 2 receives a deterministic empty input.

#### Scenario: Tour with two events → two drafts

- **WHEN** the envelope contains a `<tour>` block with two `<event>` children
- **THEN** `parseStep1Envelope` SHALL return two `EventDraft` entries
- **AND** both drafts SHALL share the same `Title` and `SourceURL` from the tour's children

#### Scenario: Standalone block → one draft

- **WHEN** the envelope contains a `<standalone>` block with one `<event>` child
- **THEN** `parseStep1Envelope` SHALL return one `EventDraft`
- **AND** the draft's `Title` and `SourceURL` SHALL come from the standalone's children

#### Scenario: Unparseable input → empty result, no error

- **WHEN** the merged envelope is not valid XML
- **THEN** `parseStep1Envelope` SHALL return `nil` (or empty slice)
- **AND** SHALL NOT return an error

### Requirement: Step 1 slice envelopes are merged by concatenation, not URL grouping

The function `mergeAndDedupEnvelopes` SHALL combine each per-slice envelope into a single `<extracted>...</extracted>` wrapper by extracting the inner body of every per-slice `<extracted>` element via `extractedInnerRe` and concatenating those bodies. The function SHALL NOT perform URL-level grouping. Event-level deduplication SHALL occur downstream in `parseStep2Response` keyed on `(local_date, venue, start_time)`.

#### Scenario: Two slice envelopes merged

- **WHEN** two slices each emit a valid `<extracted>...</extracted>` envelope
- **THEN** `mergeAndDedupEnvelopes` SHALL return one `<extracted>...</extracted>` wrapper
- **AND** the wrapper's inner body SHALL contain the concatenation of both slices' inner content

#### Scenario: One slice emits non-XML fallback text

- **WHEN** one slice's envelope contains no parseable `<extracted>` wrapper
- **AND** another slice's envelope is valid
- **THEN** the merged wrapper SHALL contain only the valid slice's content

#### Scenario: All slices return non-XML — graceful fallback

- **WHEN** no slice contains a parseable `<extracted>` wrapper
- **AND** at least one slice returned non-empty text
- **THEN** `mergeAndDedupEnvelopes` SHALL return the first non-empty slice text verbatim (so the merged-envelope artefact is preserved for logs / observability)
- **AND** `parseStep1Envelope` SHALL produce an empty `[]EventDraft` from that non-XML body
- **AND** `runStep2Parse` SHALL short-circuit on the empty draft list and return `(nil, nil, nil)` — no Step 2 API call SHALL be issued, and `Search` SHALL return an empty `[]*entity.ScrapedConcert`

### Requirement: Step 2 receives only the JSON-coercion-relevant fields

The `step2InputEvent` payload sent to Step 2 SHALL contain exactly these fields per event: `index` (integer, the join key back to the EventDraft), `venue`, `country`, `local_date`, `start_time`, `open_time`. The fields `title` and `source_url` from the EventDraft SHALL NOT enter Step 2's input or schema.

Step 2's `responseJSONSchema` SHALL describe an object with a single `events` array. Each element SHALL be an object with exactly these properties: `index`, `admin_area`, `local_date`, `start_time`, `open_time`. All five fields SHALL be required. `additionalProperties` SHALL be false.

`admin_area` SHALL be the sub-national administrative region of the input event's venue (Japanese 都道府県, US/CA state, etc.), expressed in **local form** (e.g. `愛知県`, `東京都`, `California`) and NOT in ISO 3166-2 codes (e.g. `JP-23`). Step 2 SHALL derive it from `venue` together with `country` when the venue text does not already carry the prefecture/state prefix. Step 2 SHALL emit `""` (empty string) when the region cannot be determined with confidence — `null` SHALL NOT be emitted. The Step 2 system instruction's `adminAreaField.description` carries the same contract.

#### Scenario: Step 2 input shape

- **WHEN** Step 2 input is built from 3 EventDrafts
- **THEN** the JSON payload SHALL be a list of 3 objects
- **AND** each object SHALL have the keys `{index, venue, country, local_date, start_time, open_time}` and no others

#### Scenario: Step 2 output shape

- **WHEN** Step 2's response is parsed via `responseJSONSchema`
- **THEN** each output entry SHALL have exactly the fields `{index, admin_area, local_date, start_time, open_time}`
- **AND** `title` and `source_url` SHALL NOT appear in the schema or output

### Requirement: Step 2 tools MUST be empty; responseJSONSchema MUST be set

Step 2's `GenerateContentConfig.Tools` SHALL be empty (no `GoogleSearch`, no `URLContext`, no function tools). `GenerateContentConfig.ResponseJsonSchema` SHALL be set to `responseJSONSchema`. The `assertStepInvariants("step2_parse", cfg)` guard SHALL enforce this contract and return an internal error before the API call is issued if any invariant is violated.

#### Scenario: Step 2 request shape

- **WHEN** Step 2's request is constructed
- **THEN** `cfg.Tools` SHALL be empty
- **AND** `cfg.ResponseJsonSchema` SHALL be the configured `responseJSONSchema` (non-nil)

#### Scenario: Invariant guard rejects misconfigured Step 2

- **WHEN** `assertStepInvariants("step2_parse", cfg)` is called with non-empty Tools OR a nil schema
- **THEN** the helper SHALL return an internal error
- **AND** the caller SHALL NOT issue the Gemini API call

### Requirement: Step 2's coerced output is joined back to EventDraft by index

`parseStep2Response` SHALL parse Step 2's response into `[]step2OutputEvent` and merge each entry back with the corresponding `EventDraft` by `index`. The merge SHALL produce one `*entity.ScrapedConcert` per pair using the helper `toScrapedConcert(draft, coerced, from, attrs)`. The verbatim fields (`Title`, `SourceURL`, `Venue`, `Country`) SHALL be taken from the draft; the coerced fields (`AdminArea`, `LocalDate`, `StartTime`, `OpenTime`) SHALL be taken from the Step 2 output.

If Step 2's output omits an `index` that exists in the drafts, the searcher SHALL log a WARN and skip that draft rather than abort.

#### Scenario: Index-based join — happy path

- **WHEN** Step 2 returns coerced entries for all draft indices
- **THEN** every draft SHALL produce one merged `*entity.ScrapedConcert`
- **AND** each result SHALL have its `Title` / `SourceURL` / `Venue` taken from the draft

#### Scenario: Index missing in Step 2 output → skip with WARN

- **WHEN** Step 2 omits index 3 from a 5-draft input
- **THEN** the searcher SHALL log a WARN identifying the missing index and draft title
- **AND** SHALL produce 4 merged results, not 5
- **AND** SHALL NOT return an error

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

### Requirement: SearchMetadata exposes Step1Grounded and Step2Parse

`SearchMetadata` SHALL expose two `*PassMetadata` fields populated per call:

- `Step1Grounded` — aggregated metadata across all parallel Step 1 slices (sum of token counts, OR-ed finish reasons, concatenated raw response text).
- `Step2Parse` — Step 2 metadata when Step 2 ran. SHALL be nil in any path where Step 2 did not run, namely: (a) every Step 1 slice exhausted its transient retry policy, (b) `Search` aborted because at least one Step 1 slice returned a permanent error, or (c) `parseStep1Envelope` produced an empty `[]EventDraft` and `runStep2Parse` short-circuited.

The top-level token counters and `RawResponseText` on `SearchMetadata` SHALL mirror `Step2Parse` once Step 2 completes (back-compat with existing log consumers). The harness raw-response writer SHALL emit per-step sub-objects under the JSON keys `step1_grounded` and `step2_parse`.

The fields `Step1Search`, `Step2Extract`, and `Step3Parse` SHALL NOT appear on `SearchMetadata`.

#### Scenario: Both steps succeed

- **WHEN** Step 1 and Step 2 both complete
- **THEN** `md.Step1Grounded` SHALL be non-nil with summed slice tokens
- **AND** `md.Step2Parse` SHALL be non-nil with Step 2's tokens
- **AND** the top-level mirrors SHALL reflect `Step2Parse`

#### Scenario: All Step 1 slices exhaust retries

- **WHEN** every Step 1 slice exhausts its transient retry policy
- **THEN** `md.Step1Grounded` SHALL be non-nil with the aggregated failure metadata
- **AND** `md.Step2Parse` SHALL be nil

### Requirement: A/B harness emits per-step sub-objects in raw response files

The integration test `searcher_integration_test.go`'s `writeRawResponse` SHALL persist each Gemini call's metadata under a step label. The raw response JSON SHALL contain at least the keys `step1_grounded` and `step2_parse`, each holding a serialised `PassMetadata` for that step. The CSV row writer SHALL include per-step cost columns (`step1_cost`, `step2_cost`) and a summed `cost_usd`.

#### Scenario: Per-cell raw response JSON shape

- **WHEN** a smoke cell completes
- **THEN** the per-cell raw file SHALL contain `step1_grounded` and `step2_parse` keys at the top level
- **AND** each key's value SHALL contain `prompt_tokens`, `candidates_tokens`, `total_tokens`, and `cost_usd`

### Requirement: cmd/smoke-diff reports per-event evaluation breakdown for a single smoke run

The backend SHALL provide a `cmd/smoke-diff` Go command that consumes one A/B-harness raw artifact (`cell_*.json`) plus the `testdata/ab_ground_truth.json` fixture and prints a per-event breakdown of one artist's discovered events partitioned into four buckets: MATCH (in fixture and smoke), MISS (in fixture, not in smoke), FALSE_POSITIVE (in smoke, not in fixture), TIME_MISMATCH (date and venue match but `start_time` differs). The tool SHALL exit 0 regardless of bucket counts (it is observation-only, not a CI gate) and SHALL accept a `-json` flag to additionally emit a machine-readable JSON object alongside the human-readable summary.

`recall_pct` and `precision_pct` SHALL be computed as:

```
recall_pct    = 100 × MATCH / (MATCH + MISS + TIME_MISMATCH)
precision_pct = 100 × MATCH / (MATCH + FALSE_POSITIVE)
```

That is, TIME_MISMATCH counts against recall (the fixture event was not delivered with its expected time) but does not count against precision (the smoke event is not spurious; only its time field is wrong). Both ratios SHALL be rounded to one decimal place in the human-readable summary and emitted as `float64` in the JSON output. The 86.4% / 100% values that appear in the BRADIO scenario below presume `TIME_MISMATCH = 0` for that run; with any non-zero TIME_MISMATCH the recall would drop by `100 / (MATCH + MISS + TIME_MISMATCH)` per misclassified event.

This requirement formalises the ad-hoc `jq` + `comm` shell pipelines that were used during the 4-artist post-cleanup smoke (UVERworld / Vaundy / BRADIO / SUPER BEAVER) so future contributors can reproduce the per-event analysis with a single command instead of reconstructing the shell incantations from session transcripts. That smoke recorded an aggregate effective recall of 92 / 95 at 100% precision, counting Vaundy's three HK/KR time-zone extraction misses as date-level matches; the strict (date+time) count for the same run is 89 / 95 (93.7%), per design.md's smoke summary.

#### Scenario: Human-readable breakdown for an 86%-recall cell

- **WHEN** `go run ./cmd/smoke-diff -fixture=testdata/ab_ground_truth.json -smoke=testdata/ab_results/<ts>_raw/cell_001_*_BRADIO_*.json -artist=BRADIO` is invoked against a smoke artifact with 19 discovered concerts and a fixture containing 22 BRADIO in-scope events
- **THEN** stdout SHALL contain one section per bucket, each listing the affected events' `(local_date, start_time, venue, title)`
- **AND** the final summary line SHALL show `Recall: 86.4% | Precision: 100%` (or the equivalent computed ratio)
- **AND** the exit code SHALL be 0 regardless of the bucket counts

#### Scenario: Machine-readable JSON output

- **WHEN** `cmd/smoke-diff` is invoked with `-json` against the same inputs
- **THEN** stdout SHALL also contain a JSON object whose top-level keys are `matched`, `missed`, `false_positives`, `time_mismatches`, `recall_pct`, `precision_pct`
- **AND** each event element under the four list keys SHALL contain `local_date`, `start_time`, `venue`, `title`, `source_url` (empty string when the source value is empty)

#### Scenario: TIME_MISMATCH classification distinct from MISS

- **WHEN** the smoke artifact records an event whose `local_date` and `venue` match a fixture entry but whose `start_time` differs (e.g. smoke has empty `start_time` while fixture has `2026-10-03T20:00:00+08:00`)
- **THEN** that event SHALL be classified as `TIME_MISMATCH`, not `MISS` and not `FALSE_POSITIVE`
- **AND** the breakdown summary SHALL count it under the time-mismatch bucket only
