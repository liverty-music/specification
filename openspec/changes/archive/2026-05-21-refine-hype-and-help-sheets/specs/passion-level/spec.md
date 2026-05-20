## MODIFIED Requirements

### Requirement: Passion Level Tiers

The system SHALL support four hype level tiers for each followed artist. The tier surface labels are Layer B brand expressions (per the `brand-vocabulary` capability) rendered invariantly in English across all locales:

| Tier | Proto Value | Emoji | UI Label (invariant, all locales) | Notification Scope |
|------|-------------|-------|------------------------------------|-------------------|
| Watch | HYPE_TYPE_WATCH | 👀 | Watch | None |
| Home | HYPE_TYPE_HOME | 🔥 | Home | Home area only |
| Nearby | HYPE_TYPE_NEARBY | 🔥🔥 | Nearby | Within 200km |
| Away | HYPE_TYPE_AWAY | 🔥🔥🔥 | Away | All concerts |

All four tiers SHALL be selectable by authenticated users via the SetHype RPC. No tier SHALL be rejected by server-side validation.

#### Scenario: Default hype level on follow

- **WHEN** a user follows a new artist
- **AND** the follow relationship is created (a new row is inserted into the `followed_artists` table)
- **THEN** the hype level SHALL default to Nearby (HYPE_TYPE_NEARBY)
- **AND** the database column `followed_artists.hype` SHALL have its DEFAULT clause set to `'nearby'`, so the default is honored even when the `Follow` RPC carries no `hype` field

#### Scenario: UI labels are invariant English across locales

- **WHEN** hype level labels are displayed in any UI surface (my-artists table column header, page-help tier explanation, settings, accessibility names, slider legend)
- **THEN** the system SHALL display the invariant English forms `Watch / Home / Nearby / Away` regardless of the active locale
- **AND** the system SHALL NOT display the legacy JA-only forms `チェック / 地元 / 近くも / どこでも！` or `観測 / 地元 / 近郊 / 全国`
- **AND** the labels SHALL NOT be sourced from `entity.hype.values.*` i18n keys (which have been removed per the `brand-vocabulary` graduation to Layer B)

## ADDED Requirements

### Requirement: Existing follow records preserve their stored hype

The change to the database column default SHALL be forward-looking only. Existing `followed_artists` rows whose `hype` column holds any value (including the previous `'watch'` default) SHALL retain that value; no `UPDATE` statement SHALL run as part of the migration.

#### Scenario: Pre-migration follows keep their hype

- **WHEN** a `followed_artists` row exists with `hype = 'watch'` before the migration applies
- **AND** the migration runs (`ALTER COLUMN hype SET DEFAULT 'nearby'`)
- **THEN** the row's `hype` value SHALL remain `'watch'` after the migration
- **AND** the user's view of that follow SHALL be unaffected

#### Scenario: Post-migration new follows pick up new default

- **WHEN** the migration has been applied
- **AND** a new follow is created via the `Follow` RPC (no `hype` field in the request)
- **THEN** the newly-inserted row SHALL have `hype = 'nearby'`
- **AND** subsequent `ListFollowed` calls SHALL return that follow with `hype = HYPE_TYPE_NEARBY`
