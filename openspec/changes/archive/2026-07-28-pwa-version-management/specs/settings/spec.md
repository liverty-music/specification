## ADDED Requirements

### Requirement: Settings SHALL display the app release version in the About section

The Settings screen's existing "情報" (About) section SHALL include a version row as its last item, after the OSS Licenses row. The row SHALL display the release version sourced from `AppConfig.releaseVersion`. Both authenticated and guest users SHALL see this row. The row SHALL be read-only — no navigation occurs on tap — but tapping it SHALL copy the `releaseVersion` string to the clipboard as a support affordance.

#### Scenario: Version row displays release version

- **WHEN** the Settings page is rendered
- **AND** `AppConfig.releaseVersion` is present (e.g., `"v1.28.0"`)
- **THEN** the About section SHALL display a "バージョン / Version" label and the release version string (e.g., `v1.28.0`) as the last row

#### Scenario: Version row displays placeholder when releaseVersion is absent

- **WHEN** the Settings page is rendered
- **AND** `AppConfig.releaseVersion` is `undefined` or absent
- **THEN** the version display SHALL show `—` (em dash) as a placeholder

#### Scenario: Tapping version row copies version string to clipboard

- **WHEN** the user taps the version row
- **THEN** `releaseVersion` (or `—` if absent) SHALL be written to the system clipboard via `navigator.clipboard.writeText`
- **AND** a confirmation Snack SHALL be published

#### Scenario: Version row is visible for guest users

- **WHEN** the Settings page is rendered for an unauthenticated (guest) user
- **THEN** the version row SHALL be visible
- **AND** the version information SHALL be displayed identically to the authenticated user view
