## ADDED Requirements

### Requirement: Postmark Server API Token in Pulumi ESC

The Postmark Server API Token SHALL be stored in Pulumi ESC at the environment level (not common) under `pulumiConfig.postmark.serverApiToken` as a secret. Postmark uses the same token as both the SMTP username and password, so a single config field is sufficient.

#### Scenario: Setting dev Postmark token

- **WHEN** configuring the dev environment
- **THEN** `esc env set liverty-music/dev pulumiConfig.postmark.serverApiToken "<value>" --secret` stores the Postmark Server API Token as encrypted

#### Scenario: Setting prod Postmark token

- **WHEN** configuring the prod environment
- **THEN** `esc env set liverty-music/prod pulumiConfig.postmark.serverApiToken "<value>" --secret` stores the Postmark Server API Token as encrypted

#### Scenario: Credentials are not in GCP Secret Manager

- **WHEN** the Postmark Server API Token is needed
- **THEN** it SHALL be consumed directly by Pulumi via ESC config
- **AND** it SHALL NOT be provisioned as a GCP Secret Manager secret (Zitadel Cloud connects to SMTP directly, not via K8s pods)
