<!-- spec: admin-area-normalization | target: components/usecase/concert/create-from-discovered | flags: CLASSNAME | new_name: Normalization in Concert Discovery Pipeline -->

### Requirement: Normalization in Concert Discovery Pipeline

The concert discovery pipeline SHALL normalize Gemini's free-text `admin_area` output to an ISO 3166-2 code before persisting venue data.

#### Scenario: Gemini returns recognizable admin_area

- **WHEN** the Gemini concert searcher returns a scraped event with `admin_area = "愛知県"`
- **THEN** the pipeline SHALL normalize the value to `JP-23` before creating or updating the venue record

#### Scenario: Gemini returns unrecognizable admin_area

- **WHEN** the Gemini concert searcher returns a scraped event with an unrecognizable `admin_area`
- **THEN** the pipeline SHALL set `admin_area` to NULL on the venue record

#### Scenario: Gemini prompt unchanged

- **WHEN** the Gemini concert searcher constructs its prompt
- **THEN** the prompt text and response schema SHALL remain unchanged from the current implementation
- **AND** normalization SHALL occur after parsing the Gemini response, not within the LLM interaction
