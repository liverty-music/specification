## MODIFIED Requirements

### Requirement: GCPConfig exposes per-step Gemini search model fields

`pkg/config.GCPConfig` SHALL expose exactly two per-step Gemini search model fields, each populated from a dedicated environment variable with a fallback to a step-specific default constant:

| Field | Env var | Default constant |
|-------|---------|------------------|
| `GeminiSearchModelExtract` | `GCP_GEMINI_SEARCH_MODEL_EXTRACT` | `defaultSearchModelExtract = "gemini-3.6-flash"` |
| `GeminiSearchModelParse` | `GCP_GEMINI_SEARCH_MODEL_PARSE` | `defaultSearchModelParse = "gemini-3.1-flash-lite"` |

No `GeminiSearchModelDiscovery` field SHALL exist on `GCPConfig`. No `defaultSearchModelDiscovery` constant SHALL exist. No `GCP_GEMINI_SEARCH_MODEL_DISCOVERY` env var SHALL be read.

#### Scenario: Field set populated from env

- **WHEN** the environment provides `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.6-flash` and `GCP_GEMINI_SEARCH_MODEL_PARSE=gemini-3.1-flash-lite`
- **THEN** `GCPConfig.GeminiSearchModelExtract` SHALL be `"gemini-3.6-flash"`
- **AND** `GCPConfig.GeminiSearchModelParse` SHALL be `"gemini-3.1-flash-lite"`

#### Scenario: Discovery env var is unread

- **WHEN** the environment provides `GCP_GEMINI_SEARCH_MODEL_DISCOVERY=anything`
- **THEN** no `GCPConfig` field SHALL be populated from that variable
- **AND** the variable SHALL be ignored

#### Scenario: Extract-step default is gemini-3.6-flash

- **WHEN** `GeminiSearchModelExtract` is empty and `SearchModelExtract()` is called
- **THEN** the method SHALL return `"gemini-3.6-flash"`
