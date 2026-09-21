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
