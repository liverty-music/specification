## ADDED Requirements

### Requirement: Backend SA has service usage permission
The backend-app service account SHALL have the `roles/serviceusage.serviceUsageConsumer` IAM role bound at the project level, granting `serviceusage.services.use` permission required for OAuth-authenticated API calls with `X-Goog-User-Project` billing attribution.

#### Scenario: Places API call succeeds with OAuth token
- **WHEN** the consumer sends a POST request to `places.googleapis.com` with a Bearer token and `X-Goog-User-Project` header
- **THEN** GCP authorizes the request and the Places API returns search results (not 403)

#### Scenario: IAM role is scoped to project level
- **WHEN** the backend-app SA IAM bindings are inspected
- **THEN** `roles/serviceusage.serviceUsageConsumer` is present alongside existing roles (logWriter, metricWriter, etc.)
