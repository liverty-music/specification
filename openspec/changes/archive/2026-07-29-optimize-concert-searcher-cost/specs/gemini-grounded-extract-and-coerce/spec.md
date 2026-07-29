## RENAMED Requirements

- FROM: `### Requirement: Step 1 fans out into three parallel slices per the default slice configuration`
- TO: `### Requirement: Step 1 runs a single grounded slice per the default slice configuration`

- FROM: `### Requirement: Step 1 instructions follow a five-step workflow in Japanese`
- TO: `### Requirement: Step 1 uses a single consolidated English extraction instruction`

- FROM: `### Requirement: Step 1 prompt template uses four positional placeholders`
- TO: `### Requirement: Step 1 prompt template uses three positional placeholders`

## MODIFIED Requirements

### Requirement: ConcertSearcher executes a two-step Gemini call sequence per Search invocation

The `ConcertSearcher.Search` method SHALL execute exactly two Gemini API calls per invocation under the `gemini-grounded-extract-and-coerce` capability: Step 1 (grounded extract) and Step 2 (JSON coerce). Step 1 MAY fan out into multiple parallel sub-calls (slices), though the default configuration is a single slice; regardless of slice count, Step 1 SHALL complete before Step 2 starts. The flattened result of Step 2 SHALL be merged Go-side with the Step 1 verbatim drafts and returned to the caller as `[]*entity.ScrapedConcert`, preserving the public signature.

#### Scenario: Happy path — Step 1 and Step 2 both succeed

- **WHEN** `Search` is called with a non-nil `OfficialSite`
- **THEN** the searcher SHALL run Step 1 across the slices defined by `defaultStep1Slices`
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

#### Scenario: Step 1 transient retry exhaustion → empty envelope flows to Step 2

- **WHEN** a Step 1 slice exhausts its retries with a transient error
- **THEN** that slice's envelope SHALL be treated as empty
- **AND** the merged envelope SHALL still flow to Step 2 with whatever content succeeded (empty overall when the sole default slice fails), yielding a deterministic result

#### Scenario: Step 2 permanent error → Search returns the error

- **WHEN** Step 2 returns a permanent error
- **THEN** the wrapped error SHALL propagate to the caller
- **AND** no partial result SHALL be returned

#### Scenario: Step 2 invalid JSON → permanent error propagates

- **WHEN** Step 2's response is not valid JSON or does not satisfy `responseJSONSchema`
- **THEN** `SearchMetadata.InvalidJSON` SHALL be set to true
- **AND** the wrapped `errInvalidJSON` SHALL propagate to the caller

### Requirement: Step 1 runs a single grounded slice per the default slice configuration

Step 1 SHALL use the slices defined in `defaultStep1Slices`. The default configuration SHALL contain exactly **one** slice, which extracts both tours and standalones in a single grounded call:

| Name | SystemInstruction | PromptTemplate | FromMonthsOffset |
|------|-------------------|----------------|------------------|
| `all` | `systemInstructionStep1` | `promptTemplateStep1` | 0 |

The slice SHALL fire a single Gemini call (the fan-out mechanism is retained so the slice count stays configurable, but the default is one). The slice base date SHALL be `time.Now().UTC()`; the slice's `from_date` SHALL be `baseDate.AddDate(0, FromMonthsOffset, 0)`, formatted as `2006-01-02`. Step 1 SHALL NOT supply an end date (`to_date`); the discovery window is open-ended into the future.

#### Scenario: Single grounded call per Search

- **WHEN** `runStep1Grounded` is entered
- **THEN** the function SHALL execute exactly one slice from `defaultStep1Slices`
- **AND** that slice SHALL call `runStep1Slice` with the shared base date
- **AND** the slice SHALL extract both tours and standalones into one `<extracted>` envelope

#### Scenario: Open-ended start-date substitution

- **WHEN** the slice prompt is constructed and base date is 2026-05-24
- **THEN** the prompt SHALL substitute `from_date = "2026-05-24"`, the artist's name, and the official-site host
- **AND** the prompt SHALL NOT contain any `to_date` / end-date value

### Requirement: Step 1 uses a single consolidated English extraction instruction

Step 1 SHALL use one system instruction `systemInstructionStep1`, written in English, that extracts both tours and standalones in a single call. The instruction SHALL follow a numbered workflow:

1. Discover the artist's concert pages from the given start date onward, using `url_context` and `google_search`, **including tour pages hosted on a domain different from the official site**.
2. Fetch each candidate page and extract the per-field XML for both tours (`<tour>`, one `<event>` per date) and standalones (`<standalone>`, one `<event>`).
3. Exclude music festivals with a multi-artist lineup. A 2–4 act named co-headliner bill (対バン) is NOT a festival and SHALL be extracted as a standalone.
4. Deduplicate on the triple `(venue, local_date, start_time)`.
5. Emit the `<extracted>` XML envelope only — no prose, no markdown.

The instruction SHALL include the XML output format (with `<extracted>`, `<tour>`, `<standalone>`, `<title>`, `<source_url>`, `<event>`) as a literal example, and SHALL preserve the verbatim-copy and page-context year-inference rules.

#### Scenario: Consolidated instruction structure

- **WHEN** `systemInstructionStep1` is loaded
- **THEN** the instruction text SHALL be in English
- **AND** SHALL instruct extraction of both `<tour>` and `<standalone>` elements within one `<extracted>` envelope
- **AND** SHALL instruct exclusion of multi-artist festivals while extracting 2–4 act co-headliner bills as standalones

#### Scenario: Off-domain tour page discovery

- **WHEN** an artist's tour has a dedicated page on a domain different from the official-site host
- **THEN** the instruction SHALL direct the model to discover and extract that tour, using the off-domain page URL as `source_url`

### Requirement: Step 1 prompt template uses three positional placeholders

Step 1 SHALL use one prompt template `promptTemplateStep1`, written in English, accepting exactly three positional placeholders in this order: `from_date`, artist name, official-site host. Each call SHALL format the template via `fmt.Sprintf`. The template SHALL request extraction of both tours and standalones occurring on or after `from_date`, SHALL exclude multi-artist festivals, and SHALL NOT contain a `to_date` / end-date placeholder.

#### Scenario: Prompt formatting

- **WHEN** `promptTemplateStep1` is formatted with `("2026-05-24", "UVERworld", "www.uverworld.jp")`
- **THEN** the result SHALL contain `2026-05-24`, `UVERworld`, and `www.uverworld.jp` literally
- **AND** the result SHALL instruct the model to extract tours and standalones on or after the start date
- **AND** SHALL exclude multi-artist festivals
- **AND** SHALL NOT contain any end-date value
