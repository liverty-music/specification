## MODIFIED Requirements

### Requirement: PWA Share Target

The frontend PWA SHALL NOT register as a share target. The Android Gmail app no longer offers a share action that can target the PWA, so the share-target ingestion path is non-functional and SHALL be removed to avoid presenting a broken entry point.

#### Scenario: Manifest has no share_target

- **WHEN** the PWA manifest is configured
- **THEN** it SHALL NOT include a `share_target` entry

#### Scenario: Service Worker does not intercept share POST

- **WHEN** the Service Worker is configured
- **THEN** it SHALL NOT register a handler that intercepts share-target POST requests

### Requirement: Email Import Wizard

The frontend SHALL retain the email import wizard code but make it unavailable to users. The wizard route SHALL NOT be reachable from navigation and SHALL present an unavailable state if accessed directly, until the email-import ingestion path is revived.

#### Scenario: Import entry is unavailable

- **WHEN** a user browses the application
- **THEN** there SHALL be no navigation entry leading to the email import wizard

#### Scenario: Direct access shows unavailable state

- **WHEN** a user navigates directly to the import wizard route
- **THEN** the application SHALL present an unavailable state rather than the functional wizard

#### Scenario: Wizard code is retained

- **WHEN** the email-import feature is later revived
- **THEN** the wizard components and RPC client SHALL still exist to be re-enabled without re-implementation
