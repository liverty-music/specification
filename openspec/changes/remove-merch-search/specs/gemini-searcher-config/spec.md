## REMOVED Requirements

### Requirement: GCPConfig exposes merch-searcher model and thinking fields

**Reason**: The merch searcher is removed, so its dedicated configuration is no longer read by any workload.

**Migration**: None. The `GeminiMerchModel` (`GCP_GEMINI_MERCH_MODEL`) and `GeminiMerchThinkingLevel` (`GCP_GEMINI_MERCH_THINKING_LEVEL`) fields, their `defaultMerchModel` / `defaultMerchThinkingLevel` defaults, the `MerchModel()` / `MerchThinking()` accessors, and their `Validate()` checks are removed. The shared `GCP_GEMINI_SEARCH_API_KEY` and `GCP_GEMINI_SEARCH_TEMPERATURE` are retained — they are used by the concert-discovery and sales-phase-discovery searchers.
