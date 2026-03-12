## Why

The venue enrichment pipeline is failing to enrich 60% of venues (196/327) because the Google Maps fallback searcher is not operational — the `GOOGLE_MAPS_API_KEY` environment variable was never provisioned to the consumer pod. Additionally, enrichment error logs are scattered across usecase, repository, and consumer layers without sufficient diagnostic attributes, making troubleshooting difficult. The Google Maps client currently uses API key authentication; switching to Workload Identity Federation (WIF) with OAuth eliminates the need for secret management and aligns with the existing GKE IAM setup.

## What Changes

- Replace Google Maps API key authentication with WIF-based OAuth (ADC + Bearer token) in the Google Maps client
- Remove `GOOGLE_MAPS_API_KEY` config dependency from the consumer application
- Grant the existing `backend-app` GCP service account permission to call the Places API
- Enable the Places API (`places-backend.googleapis.com`) in the GCP project via Pulumi
- Consolidate enrichment error logging: remove scattered logs from `enrichOne()` internals and the `MarkFailed` repository method; emit structured error logs with full diagnostic attributes at the two top-level call sites (`EnrichPendingVenues`, `EnrichOne`) and in the event consumer handler
- Add merge-specific attributes (canonical_id, duplicate_id, canonical_name, raw_name) to the merge Info log

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `venue-normalization`: Google Maps authentication method changes from API key to WIF/OAuth. Enrichment error logging consolidation requires updating the failure-logging behavior described in the enrichment scenarios.

## Impact

- **backend**: Google Maps client (`internal/infrastructure/maps/google/client.go`) switches from API key query param to `Authorization: Bearer` header with ADC. DI wiring (`internal/di/consumer.go`) removes the `cfg.GoogleMapsAPIKey` conditional — Google Maps searcher is always registered. Usecase and repo logging refactored.
- **cloud-provisioning**: Pulumi enables `places-backend.googleapis.com` API. IAM binding grants Places API access to `backend-app` SA. Consumer configmap no longer needs `GOOGLE_MAPS_API_KEY`.
- **config**: `GOOGLE_MAPS_API_KEY` field removed from `config.ConsumerConfig`.
