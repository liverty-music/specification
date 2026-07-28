## ADDED Requirements

### Requirement: GCPConfig exposes merch-searcher model and thinking fields

`pkg/config.GCPConfig` SHALL expose a merch-searcher model field and a merch-searcher thinking field, each populated from a dedicated environment variable with a fallback to a default constant:

| Field | Env var | Default constant |
|-------|---------|------------------|
| `GeminiMerchModel` | `GCP_GEMINI_MERCH_MODEL` | `defaultMerchModel = "gemini-3.6-flash"` |
| `GeminiMerchThinkingLevel` | `GCP_GEMINI_MERCH_THINKING_LEVEL` | `defaultMerchThinkingLevel = "medium"` |

`GCPConfig` SHALL expose helper methods `MerchModel() string` and `MerchThinking() string` that resolve env override → default. The `MerchSearcher` SHALL read the model and thinking level exclusively via these accessors (threaded through DI into `gemini.MerchConfig`).

#### Scenario: Merch model default applied when env unset

- **WHEN** `GeminiMerchModel` is empty and `MerchModel()` is called
- **THEN** the method SHALL return `"gemini-3.6-flash"`

#### Scenario: Merch thinking default applied when env unset

- **WHEN** `GeminiMerchThinkingLevel` is empty and `MerchThinking()` is called
- **THEN** the method SHALL return `"medium"`

#### Scenario: Merch env override honoured

- **WHEN** the environment provides `GCP_GEMINI_MERCH_MODEL=gemini-3.1-flash-lite`
- **THEN** `MerchModel()` SHALL return `"gemini-3.1-flash-lite"`
