# Follow

## Purpose

Defines the Follow entity's hype level, its valid tiers of enthusiasm for a followed artist, and the rules that determine whether a given hype level should trigger a push notification.

## Requirements

### Requirement: Hype validity check

The `Hype` type SHALL provide an `IsValid() bool` method that returns true only for the four defined values: `watch`, `home`, `nearby`, `away`.

#### Scenario: Known hype values

- **WHEN** Hype is one of HypeWatch, HypeHome, HypeNearby, HypeAway
- **THEN** IsValid returns true

#### Scenario: Unknown hype value

- **WHEN** Hype is "unknown" or an empty string
- **THEN** IsValid returns false

---

### Requirement: Hype-based notification eligibility

The `Hype` type SHALL provide a `ShouldNotify(home *Home, venueAreas map[string]struct{}, concerts []*Concert) bool` method that determines whether a follower with this hype level should receive push notifications for a batch of new concerts.

Decision rules (evaluated in order):
1. `HypeWatch` → false (never notify).
2. `HypeHome` → true only if `home` is non-nil AND `home.Level1` is non-empty AND `home.Level1` exists in `venueAreas`.
3. `HypeNearby` → true only if any concert has `ProximityHome` or `ProximityNearby` relative to `home`.
4. `HypeAway` → true (always notify).
5. Any other value → false.

#### Scenario: HypeWatch never notifies

- **WHEN** Hype is HypeWatch with any home and concerts
- **THEN** ShouldNotify returns false

#### Scenario: HypeHome matches venue area

- **WHEN** Hype is HypeHome, home.Level1="JP-13", venueAreas contains "JP-13"
- **THEN** ShouldNotify returns true

#### Scenario: HypeHome no match

- **WHEN** Hype is HypeHome, home.Level1="JP-13", venueAreas contains only "JP-27"
- **THEN** ShouldNotify returns false

#### Scenario: HypeHome with nil home

- **WHEN** Hype is HypeHome, home is nil
- **THEN** ShouldNotify returns false

#### Scenario: HypeHome with empty Level1

- **WHEN** Hype is HypeHome, home.Level1 is empty string
- **THEN** ShouldNotify returns false

#### Scenario: HypeNearby with nearby concert

- **WHEN** Hype is HypeNearby, home has centroid, a concert venue is within 200km
- **THEN** ShouldNotify returns true

#### Scenario: HypeNearby with only distant concerts

- **WHEN** Hype is HypeNearby, all concerts are beyond 200km
- **THEN** ShouldNotify returns false

#### Scenario: HypeNearby with nil home

- **WHEN** Hype is HypeNearby, home is nil
- **THEN** ShouldNotify returns false

#### Scenario: HypeAway always notifies

- **WHEN** Hype is HypeAway with any home and concerts
- **THEN** ShouldNotify returns true

#### Scenario: Unknown hype skips

- **WHEN** Hype is "unknown"
- **THEN** ShouldNotify returns false

---

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

#### Scenario: SetHype accepts all four tiers

- **WHEN** an authenticated user calls SetHype with any of the four defined hype tiers (WATCH, HOME, NEARBY, AWAY)
- **THEN** the system SHALL accept the request and persist the hype level
