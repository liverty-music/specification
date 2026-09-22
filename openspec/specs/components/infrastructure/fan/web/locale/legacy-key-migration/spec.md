# Legacy Key Migration

## Purpose

Defines how the Aurelia 2 frontend renders translated strings across JA and EN locales. Covers i18n plugin registration, the detection chain that picks the initial locale, the translation-key conventions (page-keyed vs entity-keyed), how templates and TypeScript externalize strings, locale-aware date/number formatting, runtime language switching with persistence routed by authentication state, and the shared utility that lets every component switch language through one entry point.

## Requirements

### Requirement: One-Time Migration of the Legacy guest.language Key

The startup storage-migration routine SHALL reconcile and remove the legacy `guest.language` key so existing installs converge to the single-source model. Because `guest.language` was only ever written on an explicit user language choice, its value represents higher intent than the detector cache and SHALL take precedence when the two differ. An absent `localStorage['language']` SHALL be treated as differing from a present `guest.language`, so the explicit choice is promoted even when the detector cache was previously cleared (e.g. by the authenticated-session cleanup). The migration SHALL be idempotent and safe to run on every startup. The migration SHALL run before i18next detection reads `localStorage['language']`, so a promoted value takes effect in the same session (not only on the next reload).

#### Scenario: Legacy explicit choice differs from the detector cache

- **WHEN** the application starts
- **AND** `localStorage['guest.language']` is `ja`
- **AND** `localStorage['language']` is `en`
- **THEN** the system SHALL write `ja` to `localStorage['language']`
- **AND** the system SHALL remove `localStorage['guest.language']`
- **AND** the active locale on this session SHALL render in `ja`

#### Scenario: Legacy explicit choice present but detector cache absent

- **WHEN** the application starts
- **AND** `localStorage['guest.language']` is `ja`
- **AND** `localStorage['language']` is absent (e.g. cleared by a prior authenticated session)
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
