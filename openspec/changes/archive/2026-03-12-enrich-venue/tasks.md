## 1. Cloud Provisioning — Enable Places API and IAM

- [x] 1.1 Enable `places-backend.googleapis.com` API in the GCP project via Pulumi
- [x] 1.2 Grant `backend-app` service account IAM permission for Places API access

## 2. Backend — Google Maps Client OAuth Migration

- [x] 2.1 Add `golang.org/x/oauth2` and `golang.org/x/oauth2/google` dependencies
- [x] 2.2 Refactor `google.Client` to accept an `oauth2.TokenSource` instead of API key; send `Authorization: Bearer` header and `X-Goog-User-Project` header on requests
- [x] 2.3 Update `google.Client` tests to use the new OAuth-based constructor
- [x] 2.4 Remove `GoogleMapsAPIKey` field from `config.ConsumerConfig`
- [x] 2.5 Update DI wiring (`di/consumer.go`): always register Google Maps searcher using ADC token source; remove `cfg.GoogleMapsAPIKey` conditional

## 3. Backend — Enrichment Error Logging Consolidation

- [x] 3.1 Remove transient error warn log from `enrichOne()` internals (searcher loop)
- [x] 3.2 Remove warn log from `VenueRepository.MarkFailed()`
- [x] 3.3 Enhance `EnrichPendingVenues()` error logging: add attrs `venue_id`, `raw_name`, `error`, `outcome`
- [x] 3.4 Enhance `EnrichOne()`: add error log with attrs `venue_id`, `raw_name`, `error` on transient failure
- [x] 3.5 Add error log to `VenueConsumer.Handle()` with attrs `venue_id`, `venue_name`, `error`
- [x] 3.6 Enhance merge Info log in `enrichOne()`: add attrs `canonical_name`, `raw_name`

## 4. Verification

- [x] 4.1 Run backend unit tests (`make test`)
- [x] 4.2 Run cloud-provisioning lint (`make lint`)
