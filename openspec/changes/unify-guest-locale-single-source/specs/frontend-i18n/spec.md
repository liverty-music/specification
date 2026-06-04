## ADDED Requirements

### Requirement: Anonymous Locale is a Single Source of Truth

For an anonymous (unauthenticated) session, the active i18n locale SHALL be derived from exactly one persisted source — `localStorage['language']` (the i18next detector cache). No secondary `localStorage` key SHALL shadow, mirror, or override the anonymous locale. Any reactive projection of the anonymous locale (e.g. the value a language selector binds to for its highlight) SHALL be derived from the active i18n locale, NOT from a separate persisted key, so the selector highlight can never disagree with the rendered UI.

This requirement makes the selector's data source explicit: prior to this change the selector highlight was driven by a separate `guest.language` key that could drift from the detector's `language` key, producing a UI that rendered in one locale while the selector highlighted another.

#### Scenario: Selector highlight matches the rendered locale for an anonymous user

- **WHEN** an anonymous user opens the Settings or Welcome language selector
- **AND** the active i18n locale is `en`
- **THEN** the selector SHALL highlight the `en` option
- **AND** there SHALL be no persisted state under which the selector highlights a locale different from the one the UI is rendering

#### Scenario: No secondary localStorage key backs the anonymous locale

- **WHEN** an anonymous user changes or has previously chosen a language
- **THEN** the only `localStorage` key that persists the anonymous locale SHALL be `language`
- **AND** the system SHALL NOT write a separate `guest.language` (or equivalent shadow) key

#### Scenario: Resetting guest state does not change the rendered locale

- **WHEN** anonymous guest state is reset (e.g. on tapping Login, before sign-in begins)
- **THEN** the guest home and per-page help-seen flags SHALL be cleared
- **AND** `localStorage['language']` SHALL be left intact
- **AND** the rendered locale SHALL NOT change as a result of the reset

### Requirement: One-Time Migration of the Legacy `guest.language` Key

The startup storage-migration routine SHALL reconcile and remove the legacy `guest.language` key so existing installs converge to the single-source model. Because `guest.language` was only ever written on an explicit user language choice, its value represents higher intent than the detector cache and SHALL take precedence when the two differ. The migration SHALL be idempotent and safe to run on every startup.

#### Scenario: Legacy explicit choice differs from the detector cache

- **WHEN** the application starts
- **AND** `localStorage['guest.language']` is `ja`
- **AND** `localStorage['language']` is `en`
- **THEN** the system SHALL write `ja` to `localStorage['language']`
- **AND** the system SHALL remove `localStorage['guest.language']`
- **AND** the active locale on this session SHALL render in `ja`

#### Scenario: Legacy value matches the detector cache

- **WHEN** the application starts
- **AND** `localStorage['guest.language']` is `ja`
- **AND** `localStorage['language']` is `ja`
- **THEN** the system SHALL remove `localStorage['guest.language']`
- **AND** `localStorage['language']` SHALL remain `ja`

#### Scenario: No legacy key present

- **WHEN** the application starts
- **AND** `localStorage['guest.language']` is absent
- **THEN** the migration SHALL be a no-op
- **AND** `localStorage['language']` SHALL be left unchanged
