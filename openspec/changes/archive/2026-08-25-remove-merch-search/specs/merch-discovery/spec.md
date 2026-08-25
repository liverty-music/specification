## REMOVED Requirements

### Requirement: Scheduled Merch URL Discovery Job

**Reason**: The merch-url discovery feature is retired. It provides no reliable value over the tour `source_url` that concert discovery already captures — production data shows 84% of resolved merch links were a generic storefront top or bare artist homepage (worse than the tour-specific `source_url` the fan already has) and the remaining 16% duplicated `source_url`. The feature also costs an extra grounded Gemini call per series.

**Migration**: None. There is no replacement; the tour feature page reached via `series.source_url` already surfaces goods information.

### Requirement: Candidate Selection by Earliest Event and Missing Link

**Reason**: Part of the retired merch-discovery capability.

**Migration**: None. The candidate-selection window (`GCP_MERCH_DISCOVERY_WINDOW`) and the `merch_url` NULL partition are removed with the capability.

### Requirement: Dead-Link Revalidation

**Reason**: Part of the retired merch-discovery capability.

**Migration**: None. The `MerchLivenessChecker` HTTP probe and `ClearMerchURL` reset path are removed with the capability.

### Requirement: Gemini Merch URL Resolution Restricted to Official Sources

**Reason**: Part of the retired merch-discovery capability.

**Migration**: None. The `MerchSearcher` Gemini call and its official-source prompt are removed with the capability.

### Requirement: Fill-Once Persistence of Resolved URL

**Reason**: Part of the retired merch-discovery capability.

**Migration**: None. The `series.merch_url` column and its `SetMerchURL` fill-once write path are dropped.

### Requirement: Job Resilience

**Reason**: Part of the retired merch-discovery capability.

**Migration**: None. The merch-discovery CronJob is deleted; ERROR-log alert coverage for it is removed under `app-error-log-alerting`.
