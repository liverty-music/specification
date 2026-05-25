# gemini-searcher-config Specification

## Purpose

Defines the configuration surface that wires per-step Gemini model selection into the `ConcertSearcher` workload. `GCPConfig` exposes two per-step fields — `GeminiSearchModelExtract` and `GeminiSearchModelParse` — each backed by a dedicated environment variable and a step-specific default constant. The corresponding helper methods `SearchModelExtract()` and `SearchModelParse()` resolve env override → built-in default with no legacy `SearchModel()` fallback (defaults are step-specific). Dependency injection in `internal/di/{provider,job}.go` threads the resolved model names into `gemini.Config.ModelExtract` and `gemini.Config.ModelParse`; the searcher itself reads them via `modelExtract()` / `modelParse()` accessors. No `ModelDiscovery` field exists at any layer — the abandoned three-step proposal's discovery role was absorbed by the combined `{GoogleSearch, URLContext}` Step 1 call.

## Requirements


### Requirement: GCPConfig exposes per-step Gemini search model fields

`pkg/config.GCPConfig` SHALL expose exactly two per-step Gemini search model fields, each populated from a dedicated environment variable with a fallback to a step-specific default constant:

| Field | Env var | Default constant |
|-------|---------|------------------|
| `GeminiSearchModelExtract` | `GCP_GEMINI_SEARCH_MODEL_EXTRACT` | `defaultSearchModelExtract = "gemini-3.5-flash"` |
| `GeminiSearchModelParse` | `GCP_GEMINI_SEARCH_MODEL_PARSE` | `defaultSearchModelParse = "gemini-3.1-flash-lite"` |

No `GeminiSearchModelDiscovery` field SHALL exist on `GCPConfig`. No `defaultSearchModelDiscovery` constant SHALL exist. No `GCP_GEMINI_SEARCH_MODEL_DISCOVERY` env var SHALL be read.

#### Scenario: Field set populated from env

- **WHEN** the environment provides `GCP_GEMINI_SEARCH_MODEL_EXTRACT=gemini-3.5-flash` and `GCP_GEMINI_SEARCH_MODEL_PARSE=gemini-3.1-flash-lite`
- **THEN** `GCPConfig.GeminiSearchModelExtract` SHALL be `"gemini-3.5-flash"`
- **AND** `GCPConfig.GeminiSearchModelParse` SHALL be `"gemini-3.1-flash-lite"`

#### Scenario: Discovery env var is unread

- **WHEN** the environment provides `GCP_GEMINI_SEARCH_MODEL_DISCOVERY=anything`
- **THEN** no `GCPConfig` field SHALL be populated from that variable
- **AND** the variable SHALL be ignored

### Requirement: Helper methods resolve per-step model with env-var precedence over defaults

`GCPConfig` SHALL expose helper methods `SearchModelExtract() string` and `SearchModelParse() string`. Each method SHALL resolve in this order:

1. If the corresponding step-specific field (`GeminiSearchModelExtract` / `GeminiSearchModelParse`) is non-empty, return it.
2. Otherwise, return the step-specific default constant.

No `SearchModelDiscovery()` method SHALL exist on `GCPConfig`. The legacy `SearchModel()` helper, if retained for any reason, SHALL NOT be used as a fallback inside the per-step resolvers; defaults are step-specific.

#### Scenario: Step override honoured

- **WHEN** `GeminiSearchModelExtract` is `"gemini-3.5-flash"` and `SearchModelExtract()` is called
- **THEN** the method SHALL return `"gemini-3.5-flash"`

#### Scenario: Step default applied when env unset

- **WHEN** `GeminiSearchModelExtract` is empty and `SearchModelExtract()` is called
- **THEN** the method SHALL return `defaultSearchModelExtract`

#### Scenario: No discovery helper exists

- **WHEN** the codebase is scanned for `SearchModelDiscovery`
- **THEN** the search SHALL return no matches in `pkg/config`

### Requirement: Config passes per-step models through DI into gemini.Config

`internal/di/provider.go` and `internal/di/job.go` SHALL wire `cfg.GCP.SearchModelExtract()` and `cfg.GCP.SearchModelParse()` into `gemini.Config` via fields named `ModelExtract` and `ModelParse`. Neither file SHALL reference `SearchModelDiscovery` or set a `ModelDiscovery` field on `gemini.Config`. The corresponding internal `gemini.Config.modelExtract()` and `modelParse()` accessors SHALL be the only methods used inside `searcher.go` to pick the model for each step.

#### Scenario: DI wiring

- **WHEN** the gemini searcher is constructed via `internal/di/provider.go`
- **THEN** `gemini.Config.ModelExtract` SHALL receive `cfg.GCP.SearchModelExtract()`
- **AND** `gemini.Config.ModelParse` SHALL receive `cfg.GCP.SearchModelParse()`
- **AND** no `ModelDiscovery` field SHALL be set

#### Scenario: Searcher model selection

- **WHEN** `runStep1Slice` selects a model name for the API call
- **THEN** it SHALL call `s.config.modelExtract()`

#### Scenario: Step 2 model selection

- **WHEN** `runStep2Parse` selects a model name for the API call
- **THEN** it SHALL call `s.config.modelParse()`

#### Scenario: Searcher rejects empty model name at construction

- **WHEN** `gemini.NewConcertSearcher` is called with a `Config` whose `modelExtract()` or `modelParse()` resolves to the empty string (e.g. a future DI path that drops the per-step wiring AND leaves the legacy `ModelName` empty)
- **THEN** the constructor SHALL return an error before any Gemini client is initialised
- **AND** the error message SHALL identify which per-step field was unresolved (`ModelExtract` vs `ModelParse`)
- **AND** no Gemini API call SHALL be issued for that searcher
