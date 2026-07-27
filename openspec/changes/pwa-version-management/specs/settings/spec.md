## ADDED Requirements

### Requirement: Settings SHALL display app version information in a dedicated section

The Settings screen SHALL include an "アプリ情報" (App Info) section placed at the bottom of the page, below all other sections. The section SHALL display the release version sourced from `AppConfig.releaseVersion` and a build identity SHA injected at build time via a vite `define` constant (`__BUILD_SHA__`). Both authenticated and guest users SHALL see this section. The section SHALL be read-only — no navigation occurs on tap — but tapping the version row SHALL copy a combined version string to the clipboard as a support affordance.

#### Scenario: Version row displays release version and build SHA

- **WHEN** the Settings page is rendered
- **AND** `AppConfig.releaseVersion` is present (e.g., `"v1.26.0"`)
- **THEN** the app info section SHALL display the release version string (e.g., `v1.26.0`)
- **AND** SHALL display the 7-character build SHA (e.g., `abc1234`)

#### Scenario: Version row displays placeholder when releaseVersion is absent

- **WHEN** the Settings page is rendered
- **AND** `AppConfig.releaseVersion` is `undefined` or absent
- **THEN** the release version display SHALL show `—` (em dash) as a placeholder
- **AND** the build SHA SHALL still be displayed

#### Scenario: Tapping version row copies version string to clipboard

- **WHEN** the user taps the version row
- **THEN** the combined string `<releaseVersion> (<buildSHA>)` (e.g., `v1.26.0 (abc1234)`) SHALL be written to the system clipboard via `navigator.clipboard.writeText`
- **AND** if `releaseVersion` is absent the copied string SHALL use `—` in place of the version (e.g., `— (abc1234)`)

#### Scenario: Section is visible for guest users

- **WHEN** the Settings page is rendered for an unauthenticated (guest) user
- **THEN** the app info section SHALL be visible
- **AND** the version information SHALL be displayed identically to the authenticated user view
