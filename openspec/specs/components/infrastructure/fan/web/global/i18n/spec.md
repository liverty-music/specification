# I18n

## Purpose

How the fan app chooses its language and renders localized text: resolving and detecting the language, switching it, keeping it in sync with the account, the product's vocabulary, and localized dates, numbers, area and venue names.

## Requirements

### Requirement: Unified Language Preference Resolution

The guest (anonymous-period) language preference SHALL be exposed as
observable application state, unified with the authenticated user's
`preferredLanguage` source. The frontend SHALL NOT read the active guest
language through an unobservable locale lookup at render time for the purpose
of driving UI state; bindings that depend on the current language SHALL
depend on the observable language value. The system SHALL also handle an
authenticated user whose backend preferred-language value is NULL (historical
rows not yet backfilled) by surfacing the detected locale as the effective
language and backfilling the server value via `UserService.SetPreferredLanguage`;
this fallback path is independent of the guest-data reconciliation, which
only fires when guest data is present in localStorage.

#### Scenario: Guest language exposed as observable
- **WHEN** a guest's preferred language is read for display or selection state
- **THEN** it SHALL be sourced from the observable current-language value
  (backed by the anonymous-period `language` localStorage key)
- **AND** a change to the guest language SHALL notify dependent bindings so they
  re-evaluate without a manual mirror or a render-time unobservable locale read

#### Scenario: Unified resolution across auth states
- **WHEN** the current preferred language is read
- **THEN** the system SHALL surface the authenticated user's
  `User.preferredLanguage` for an authenticated user and the anonymous-period
  language for a guest
- **AND** callers SHALL NOT branch on authentication state to choose the source

#### Scenario: NULL preferred_language surfaced and backfilled
- **WHEN** the authenticated user's `User.preferredLanguage` is NULL
- **THEN** the system SHALL surface the detected locale as the effective language
- **AND** the system SHALL backfill the server value via
  `UserService.SetPreferredLanguage`, preserving the current
  `user-hydration-task` behavior
- **AND** this SHALL occur whether or not any guest data exists in localStorage

### Requirement: Anonymous Locale is a Single Source of Truth

For an anonymous (unauthenticated) session, the active i18n locale SHALL be derived from exactly one persisted source — `localStorage['language']` (the i18next detector cache). No secondary `localStorage` key SHALL shadow, mirror, or override the anonymous locale. Any reactive projection of the anonymous locale (e.g. the value a language selector binds to for its highlight) SHALL be derived from the active i18n locale, NOT from a separate persisted key, so the selector highlight can never disagree with the rendered UI.

This requirement makes the selector's data source explicit: prior to this change the selector highlight was driven by a separate `guest.language` key that could drift from the detector's `language` key, producing a UI that rendered in one locale while the selector highlighted another.

#### Scenario: Selector highlight matches the rendered locale for an anonymous user

- **WHEN** an anonymous user opens the Settings or Welcome language selector
- **AND** the active i18n locale is `en`
- **THEN** the selector SHALL highlight the `en` option

#### Scenario: No secondary localStorage key backs the anonymous locale

- **WHEN** an anonymous user changes or has previously chosen a language
- **THEN** the only `localStorage` key that persists the anonymous locale SHALL be `language`
- **AND** the system SHALL NOT write a separate `guest.language` (or equivalent shadow) key

#### Scenario: Resetting guest state does not change the rendered locale

- **WHEN** anonymous guest state is reset (e.g. on tapping Login, before sign-in begins)
- **THEN** the guest home and per-page help-seen flags SHALL be cleared
- **AND** `localStorage['language']` SHALL be left intact
- **AND** the rendered locale SHALL NOT change as a result of the reset

---

### Requirement: Language Switching

The system SHALL re-render all translated strings when the active locale
changes without requiring a page reload, using a shared utility for changing
the active locale that selects the correct persistence path based on the
caller's authentication state, so components do not duplicate this logic.
The persistence target SHALL depend on the authentication state: anonymous
changes are saved on this device only; authenticated changes are saved to the
account via `UserService.SetPreferredLanguage` and, once applied, also on this
device per "Language Kept Across Sign-in and Sign-out".

#### Scenario: Switching language mid-session as an anonymous user
- **WHEN** an unauthenticated user changes the language preference (e.g., from the Welcome page language selector)
- **THEN** all `t`-bound template strings SHALL immediately update to the new locale
- **AND** the language saved on this device SHALL be updated
- **AND** the system SHALL NOT issue any backend RPC for the change
- **AND** date/number formatters SHALL use the new locale for subsequent renders

#### Scenario: Switching language mid-session as an authenticated user
- **WHEN** an authenticated user changes the language preference (e.g., from the Settings page)
- **THEN** the system SHALL call `UserService.SetPreferredLanguage` with the new locale
- **AND** on success, the system SHALL apply the new locale so all `t`-bound template strings update immediately
- **AND** the language saved on this device SHALL then hold the new locale
- **AND** date/number formatters SHALL use the new locale for subsequent renders

#### Scenario: Authenticated language switch RPC failure
- **WHEN** the `SetPreferredLanguage` RPC fails (network, server error)
- **THEN** the active locale SHALL end at the value it held before the change was attempted (the implementation MAY apply the new locale optimistically and revert on failure; the user-observable end-state SHALL be unchanged)
- **AND** the language saved on this device SHALL end at the value it held before the change was attempted
- **AND** the system SHALL surface a user-visible error notification (Snack)

#### Scenario: Anonymous caller path
- **WHEN** any component calls the shared language-change utility while unauthenticated
- **THEN** the utility SHALL apply the new locale and save it on this device
- **AND** the utility SHALL NOT issue any backend RPC

#### Scenario: Authenticated caller path
- **WHEN** any component calls the shared language-change utility while authenticated
- **THEN** the utility SHALL call `UserService.SetPreferredLanguage` first
- **AND** on success, the utility SHALL apply the new locale

#### Scenario: Used by both Welcome and Settings
- **WHEN** the Welcome page (anonymous context) and Settings page (authenticated context) both change language
- **THEN** they SHALL both call the same shared utility
- **AND** the utility SHALL route persistence appropriately for each context

### Requirement: Apply Preferred Language to i18n After Hydration

After loading the authenticated user's profile, the system SHALL apply the user's stored preferred language to the active i18n locale, making the DB the source of truth for authenticated sessions.

#### Scenario: Preferred language present in hydrated profile

- **WHEN** `UserService.ensureLoaded()` resolves and `UserService.current.preferredLanguage` is set
- **THEN** the system SHALL call `I18N.setLocale(UserService.current.preferredLanguage)`
- **AND** all `t`-bound template strings SHALL re-render to the resolved locale

#### Scenario: Brief locale flicker on slow networks is acceptable

- **WHEN** the application bootstraps an authenticated user
- **AND** the initial i18n chain (querystring → localStorage → navigator) sets a tentative locale before `ensureLoaded()` resolves
- **THEN** the system MAY render with the tentative locale until the hydration completes
- **AND** the system SHALL switch to the DB-sourced locale as soon as hydration resolves
- **AND** the system SHALL NOT block initial render waiting for hydration

### Requirement: Backfill Preferred Language When Missing

When the hydrated user profile has no preferred language set (NULL legacy row), the system SHALL backfill the DB by persisting the currently effective locale before continuing.

#### Scenario: Hydrated profile has no preferred language

- **WHEN** `UserService.ensureLoaded()` resolves
- **AND** `UserService.current.preferredLanguage` is absent (proto `optional` field not present)
- **THEN** the system SHALL call `UserService.setPreferredLanguage(I18N.getLocale())`
- **AND** on success, `UserService.current.preferredLanguage` SHALL match the value sent
- **AND** the active i18n locale SHALL remain unchanged (no flicker because the value matched what was already effective)

#### Scenario: Backfill RPC failure is non-fatal

- **WHEN** the backfill `SetPreferredLanguage` RPC fails
- **THEN** the system SHALL log a warning
- **AND** the application SHALL continue to render with the current locale
- **AND** the next hydration cycle SHALL retry the backfill (because the DB still holds NULL)

### Requirement: Timezone-based country detection
The system SHALL detect the user's country from the browser's IANA timezone identifier using `Intl.DateTimeFormat().resolvedOptions().timeZone`.

#### Scenario: Known timezone maps to a country
- **WHEN** the browser reports a recognized IANA timezone (e.g., `"Asia/Tokyo"`)
- **THEN** the system SHALL return the corresponding ISO 3166-1 country name (e.g., `"Japan"`)
- **AND** the mapping SHALL be performed synchronously without user interaction

#### Scenario: Unknown or generic timezone
- **WHEN** the browser reports `"UTC"`, `"Etc/GMT+9"`, or an unmapped timezone
- **THEN** the system SHALL return an empty string
- **AND** the caller SHALL treat empty string as "no country detected" (global fallback)

#### Scenario: API unavailable
- **WHEN** `Intl.DateTimeFormat` is not available in the browser environment
- **THEN** the system SHALL return an empty string without throwing an error

### Requirement: Mapping table coverage
The system SHALL maintain a static mapping table covering major IANA timezones for countries with meaningful Last.fm chart data.

#### Scenario: Mapping table entries
- **WHEN** the mapping table is consulted
- **THEN** it SHALL include at minimum the following timezone-to-country mappings:
  - `Asia/Tokyo` → `Japan`
  - `America/New_York`, `America/Chicago`, `America/Denver`, `America/Los_Angeles` → `United States`
  - `Europe/London` → `United Kingdom`
  - `Europe/Berlin`, `Europe/Paris`, `Europe/Rome`, `Europe/Madrid` → their respective countries
  - `Asia/Seoul` → `South Korea`
  - `Australia/Sydney`, `Australia/Melbourne` → `Australia`
  - `America/Toronto`, `America/Vancouver` → `Canada`
  - `America/Sao_Paulo` → `Brazil`

### Requirement: Locale-Aware Date and Number Formatting
The system SHALL format dates and numbers according to the active locale instead of hardcoding `ja-JP`.

#### Scenario: Date formatting follows active locale
- **WHEN** a date is displayed using the date ValueConverter
- **THEN** the system SHALL use `@aurelia/i18n`'s `df` ValueConverter or `Intl.DateTimeFormat` with the active i18next language
- **AND** JA locale SHALL display dates in Japanese format (e.g., `3月15日`)
- **AND** EN locale SHALL display dates in English format (e.g., `Mar 15`)

#### Scenario: Relative time formatting follows active locale
- **WHEN** a relative time is displayed (e.g., "3 days ago")
- **THEN** the system SHALL use `Intl.RelativeTimeFormat` with the active i18next language

---

### Requirement: Two-Layer Vocabulary Model
The system SHALL classify every user-facing term into one of two layers based on whether the term corresponds to a protobuf entity definition.

#### Scenario: Term refers to a protobuf entity
- **WHEN** a user-facing term refers to a concept that is defined as a protobuf message, enum, or enum value in `specification/proto/`
- **THEN** the term SHALL be managed under Layer A (entity-grounded labels)
- **AND** its label SHALL live in the frontend i18n JSON under the `entity.*` namespace

#### Scenario: Term has no entity backing
- **WHEN** a user-facing term is a coined brand expression, marketing phrase, lane name, or product noun that has no corresponding protobuf entity
- **THEN** the term SHALL be managed under Layer B (brand expressions)
- **AND** its canonical JA and EN forms SHALL be listed in `openspec/specs/brand-vocabulary/spec.md`

#### Scenario: Layer B term becomes entity-modeled
- **WHEN** a Layer B term is later modeled as a protobuf entity
- **THEN** the term SHALL be migrated to Layer A
- **AND** the corresponding row SHALL be removed from this spec's brand expression table

---

### Requirement: Asymmetric Locale Labels
The system SHALL allow JA and EN entries under the same `entity.*` key to use different surface words, treating asymmetric localization as a normal i18n choice rather than a defect.

#### Scenario: Lint accepts asymmetric values
- **WHEN** the brand-vocabulary lint script runs against an `entity.*` key whose JA and EN values differ in meaning (not just spelling)
- **THEN** the script SHALL NOT flag the difference as an error

---

### Requirement: Deprecated Colloquial Terms

The system SHALL maintain a registry of colloquial Japanese terms whose use in user-facing copy is forbidden in favor of entity-grounded vocabulary, and SHALL provide the canonical replacement guidance for each.

> **Enforcement model**: This requirement is normative (the `SHALL NOT` clauses below are binding on any change to JA user-facing copy). Until the `check-brand-vocabulary` lint script is extended to flag arbitrary banned tokens (currently it enforces `entity.*` JA/EN parity only), enforcement relies on (a) the registry below acting as the single source of truth and (b) reviewer attention during PR review. The follow-up to add automated token scanning is tracked separately and does not block any change that respects the rules.

#### Scenario: 推し is deprecated in favor of entity-grounded vocabulary

- **WHEN** authoring or reviewing JA user-facing copy in `frontend/src/locales/ja/translation.json`
- **THEN** the token `推し` SHALL NOT appear as a noun standing in for "artist a user follows"
- **AND** the noun SHALL be expressed as `アーティスト` (mapping to the protobuf `Artist` entity)
- **AND** the act of marking an artist as followed SHALL be expressed with the verb `フォローする` (mapping to the `FollowService.Follow` RPC semantics)
- **AND** typical surface forms SHALL follow these patterns:
  - CTA verb phrase: `アーティストをフォローする`
  - Outcome phrase: `フォローしたアーティストの<…>`
  - Possessive phrase: `好きなアーティストの<…>` (when the relationship has not yet been formalized as a follow)

#### Scenario: Registry of deprecated terms maintained in this spec

- **WHEN** this requirement is in effect
- **THEN** this spec SHALL list every deprecated colloquial JA term alongside its canonical replacement guidance
- **AND** the initial registry SHALL contain at least:
  - `推し` → noun `アーティスト` (Layer A, entity-grounded) + verb `フォローする`

#### Scenario: Adding a new deprecated term

- **WHEN** the team agrees that a previously-used JA colloquial term is no longer acceptable in user-facing copy
- **THEN** a row SHALL be added to this spec's deprecated-terms registry before or alongside the change that removes its remaining usages
- **AND** the row SHALL state the deprecated token and its canonical replacement guidance

---

### Requirement: Brand Expression Registry
The system SHALL maintain a single registry table in this spec listing every Layer B brand expression with its canonical JA and EN forms.

#### Scenario: Initial registry contents
- **WHEN** this spec is interpreted at the current revision
- **THEN** the registry SHALL include the following Layer B expressions, each with identical JA and EN surface forms unless otherwise noted:
  - `Product name — full form` — JA: `Liverty Music` / EN: `Liverty Music` (used in the HTML `<title>`, the web app manifest `name` member, and prose)
  - `Product name — home-screen short form` — JA: `LivertyMusic` / EN: `LivertyMusic` (the web app manifest `short_name` member, chosen without a space to minimize home-screen label truncation)
  - `Navigation tab — Timetable` — JA: `Timetable` / EN: `Timetable`
  - `Navigation tab — Discovery` — JA: `Discovery` / EN: `Discovery`
  - `Navigation tab — My Artists` — JA: `My Artists` / EN: `My Artists`
  - `Navigation tab — Tickets` — JA: `Tickets` / EN: `Tickets`
  - `Navigation tab — Settings` — JA: `Settings` / EN: `Settings`
  - `Personal timetable promise` — JA: `あなただけのタイムテーブル` / EN: `your personal timetable`
  - `HOME STAGE lane` — JA: `HOME STAGE` / EN: `HOME STAGE`
  - `NEAR STAGE lane` — JA: `NEAR STAGE` / EN: `NEAR STAGE`
  - `AWAY STAGE lane` — JA: `AWAY STAGE` / EN: `AWAY STAGE`
  - `Hype concept label` — JA: `Hype` / EN: `Hype`
  - `Hype tier — Watch` — JA: `Watch` / EN: `Watch`
  - `Hype tier — Home` — JA: `Home` / EN: `Home`
  - `Hype tier — Nearby` — JA: `Nearby` / EN: `Nearby`
  - `Hype tier — Away` — JA: `Away` / EN: `Away`

#### Scenario: Navigation tab labels are invariant across locales
- **WHEN** a navigation tab label is rendered in any UI surface (bottom navigation bar or a route's page header)
- **THEN** the label SHALL be the invariant English form from the registry, identical in JA and EN locales
- **AND** a route's page header SHALL bind the shared `nav.*` label rather than a separate localized title key

#### Scenario: Adding a new brand expression
- **WHEN** a new coined phrase is introduced into user-facing copy
- **AND** the phrase has no corresponding protobuf entity
- **THEN** a row SHALL be added to this spec's registry table before or alongside the change that introduces the phrase

#### Scenario: Removing a graduated expression
- **WHEN** a Layer B expression becomes entity-modeled and is migrated to Layer A
- **THEN** its row SHALL be removed from this spec's registry table in the same change that performs the migration

#### Scenario: Japanese gloss is prose, not label
- **WHEN** a Japanese-locale help or descriptive sentence introduces a Layer B brand expression that may be unfamiliar to first-time JA readers (e.g. `Hype`)
- **THEN** the sentence MAY include a parenthetical gloss (e.g. `Hype（熱量）`) inline within the prose
- **AND** the gloss SHALL NOT be promoted to the canonical surface label or stored as a separate i18n key

#### Scenario: Registry SHALL NOT include deprecated colloquial terms

- **WHEN** a colloquial JA term (such as `推し`) is identified as deprecated per the Deprecated Colloquial Terms requirement
- **THEN** the term SHALL NOT be listed in the Layer B brand expression registry
- **AND** the term SHALL instead be tracked in the deprecated-terms registry with its canonical entity-grounded replacement

### Requirement: Hype Tier Surface Labels Are Layer B
The system SHALL treat the four hype tier surface labels (`Watch`, `Home`, `Nearby`, `Away`) and the Hype concept label itself as Layer B brand expressions rendered invariantly across JA and EN locales, NOT as Layer A entity-grounded labels.

#### Scenario: Hype tier label is invariant English
- **WHEN** any UI surface (help sheet, table column header, slider legend, prose) renders a hype tier label
- **THEN** the surface form SHALL be one of `Watch`, `Home`, `Nearby`, `Away` regardless of the active locale
- **AND** the surface form SHALL NOT be sourced from an `entity.hype.values.*` i18n key
- **AND** the JA-only tier translations (`観測`, `地元`, `近郊`, `全国`) SHALL NOT appear anywhere in user-facing copy

#### Scenario: Hype concept label is invariant English
- **WHEN** any UI surface labels the four-tier concept itself (e.g. as a column-group label, a help sheet section title prefix, an accessibility name)
- **THEN** the surface form SHALL be `Hype` regardless of the active locale
- **AND** the surface form SHALL NOT be sourced from an `entity.hype.label` i18n key
- **AND** the JA-only concept label `Stage` SHALL NOT appear as a label for the Hype concept

#### Scenario: Lint script does not enforce parity on Hype keys
- **WHEN** the brand-vocabulary lint script processes the translation files
- **THEN** the script SHALL NOT require `entity.hype.label` or `entity.hype.values.*` to exist in either locale
- **AND** the script SHALL flag any newly-introduced `entity.hype.*` key as a vocabulary-layer violation (Layer A namespace used for what is now a Layer B concept)

---

### Requirement: Display localized admin-area names

The frontend SHALL convert ISO 3166-2 codes to human-readable names for display, using the browser's locale for language selection.

#### Scenario: Display admin_area in venue detail

- **WHEN** a venue's `admin_area` ISO 3166-2 code is displayed to the user
- **THEN** the frontend SHALL render the localized name (e.g., `JP-13` → "東京都" for `ja`, "Tokyo" for `en`)

#### Scenario: Display home area in region setup

- **WHEN** the region setup sheet presents area options to the user
- **THEN** the options SHALL display localized names
- **AND** the selected value sent to the backend SHALL be structured as a `Home` message with `country_code` and `level_1`

### Requirement: Concert admin-area shown as localized label

The presentation `Concert` entity SHALL expose the venue's administrative area only as a human-readable, localized display label (`locationLabel`). It SHALL NOT carry the raw ISO 3166-2 subdivision code. The mapping layer that translates RPC responses into presentation entities is the single point that translates the venue's `admin_area` code into the display label; presentation code SHALL consume `locationLabel` and SHALL NOT re-derive the label from a raw code.

#### Scenario: Mapper produces only the display label

- **WHEN** the RPC mapper maps a proto `Concert` whose `venue.admin_area` is a known code (e.g. `JP-13`)
- **THEN** the resulting entity SHALL set `locationLabel` to the localized name (e.g. `東京都`)
- **AND** the entity SHALL NOT expose the raw `JP-13` code

#### Scenario: Missing admin area yields empty label

- **WHEN** the proto `Concert` has no `venue.admin_area`
- **THEN** the entity's `locationLabel` SHALL be an empty string
- **AND** consumers SHALL treat the empty string as "no administrative area to display"

#### Scenario: Presentation consumes the label, not a code

- **WHEN** a component needs the administrative area for display or for composing a derived value (e.g. a Google Maps query)
- **THEN** it SHALL read `locationLabel`
- **AND** it SHALL NOT call the code-to-name normalization helper to re-derive the label

### Requirement: Venue name display respects user's preferred language

The concert mapper SHALL select the venue display name based on the user's current language setting. For Japanese users, `listed_venue_name` (scraped from the artist's official site, typically Japanese) SHALL be preferred over `venue.name` (Google Places canonical). For English users, `venue.name` SHALL be preferred. Either direction SHALL fall back to the other field when the preferred field is absent.

#### Scenario: Japanese user sees listed_venue_name when available

- **WHEN** the concert mapper resolves the venue display name
- **AND** the user's current language is `ja`
- **AND** the concert has a non-empty `listed_venue_name`
- **THEN** the mapper SHALL use `listed_venue_name` as the venue display name

#### Scenario: Japanese user falls back to venue.name when listed_venue_name is absent

- **WHEN** the concert mapper resolves the venue display name
- **AND** the user's current language is `ja`
- **AND** the concert has no `listed_venue_name` (null or empty)
- **THEN** the mapper SHALL use `venue.name` as the venue display name

#### Scenario: English user sees venue.name when available

- **WHEN** the concert mapper resolves the venue display name
- **AND** the user's current language is `en`
- **AND** the concert's embedded venue has a non-empty `name`
- **THEN** the mapper SHALL use `venue.name` as the venue display name

#### Scenario: English user falls back to listed_venue_name when venue.name is absent

- **WHEN** the concert mapper resolves the venue display name
- **AND** the user's current language is `en`
- **AND** the concert's embedded venue has no name
- **THEN** the mapper SHALL use `listed_venue_name` as the venue display name

#### Scenario: Language parameter is injected into the mapper

- **WHEN** the concert mapper function (or class) is invoked
- **THEN** it SHALL accept the current language as an explicit parameter
- **AND** it SHALL NOT read the language directly from a global store or singleton

### Requirement: Language Kept Across Sign-in and Sign-out

The language the fan app shows SHALL be saved on this device every time it is applied, whether the user is a guest or signed in: a guest's switch, the detected language on first open, an account's preferred language applied after sign-in, and a signed-in switch from Settings. Signing in, signing out and an involuntary logout SHALL NOT clear the saved language, so the first screen after any of them opens in the language that was shown just before.

#### Scenario: Welcome after sign-out keeps the account's language

- **WHEN** a signed-in fan whose account language is `ja` signs out on a browser whose preferred language is English
- **THEN** the Welcome page after the sign-out redirect is in Japanese
- **AND** a reload of the Welcome page is still in Japanese

#### Scenario: Sign-out after a reload keeps the language

- **WHEN** a signed-in fan whose account language is `ja` reloads the app, and then signs out
- **THEN** the Welcome page after the sign-out redirect is in Japanese

#### Scenario: Language switched while signed in survives sign-out

- **WHEN** a signed-in fan switches the language from `ja` to `en` in Settings and then signs out
- **THEN** the Welcome page after the sign-out redirect is in English

#### Scenario: Involuntary logout keeps the language

- **WHEN** a signed-in fan whose account language is `ja` is logged out because the session can no longer be renewed
- **THEN** the page shown after the logout is in Japanese

### Requirement: Hosted Login Opens in the App's Language

Every redirect from the fan app to the hosted login screen (Login and Sign up, from any screen that offers them) SHALL ask the hosted login to show the language the fan app is showing at that moment. The hosted login's own handling of that request is specified in the fan hosted-login surface.

#### Scenario: Login from the Welcome page in Japanese

- **WHEN** a guest who switched the Welcome page to Japanese taps Login on a browser whose preferred language is English
- **THEN** the hosted login screen opens in Japanese

#### Scenario: Sign up in English

- **WHEN** a guest viewing the app in English taps Sign up on a browser whose preferred language is Japanese
- **THEN** the hosted sign-up screen opens in English

### Requirement: Page Declares the Language Shown

The fan app's page SHALL always declare the language it is showing, so that screen readers, the browser's translation offer and hyphenation follow it. The declared language SHALL change together with the shown language: on first open, after the account's language is applied, and on every switch, without a reload.

#### Scenario: English shown on first open

- **WHEN** a guest opens the fan app for the first time in a browser whose preferred language is English
- **THEN** the page declares English

#### Scenario: Switch updates the declared language

- **WHEN** a guest switches the Welcome page from English to Japanese
- **THEN** the page declares Japanese without a reload

#### Scenario: Account language applied after sign-in

- **WHEN** a signed-in user whose account language is `ja` opens the app with English saved on this device
- **THEN** the page declares Japanese once the account is loaded

### Requirement: Language Chosen on First Open
The system SHALL choose the language on first open with one rule: the language chosen in the app and saved on this device, else the browser's preferred language when it is Japanese or English, else English. A `?lang=` URL parameter SHALL override the rule for that open. The chosen language SHALL be saved on this device so that later opens do not re-detect. The rule runs before a signed-in user's account is loaded, so its result is a TENTATIVE initial language for a signed-in session: once the account is loaded, its preferred language replaces it per "Account Language Wins While Signed In".

#### Scenario: URL parameter override
- **WHEN** the URL contains a `?lang=en` query parameter
- **THEN** the system SHALL set the active locale to EN regardless of other settings
- **AND** the system SHALL save `en` on this device

#### Scenario: Saved language (tentative initial locale)
- **WHEN** no `?lang=` URL parameter is present
- **AND** the language saved on this device is `en`
- **THEN** the system SHALL set the active locale to EN as the tentative initial value
- **AND** for an anonymous session, this tentative value SHALL be the final active locale
- **AND** for an authenticated session, this tentative value SHALL be replaced by the account's preferred language as soon as the account is loaded

#### Scenario: Browser language detection is saved
- **WHEN** no `?lang=` URL parameter is present
- **AND** no language is saved on this device
- **AND** the browser's preferred language is English (e.g. `en-US`)
- **THEN** the system SHALL set the active locale to EN
- **AND** the system SHALL save `en` on this device so subsequent reloads do not re-detect

#### Scenario: Fallback to English
- **WHEN** no `?lang=` URL parameter is present
- **AND** no language is saved on this device
- **AND** the browser's preferred language is neither Japanese nor English (e.g. `fr`)
- **THEN** the system SHALL set the active locale to EN
- **AND** the system SHALL save `en` on this device

#### Scenario: New account from an unsupported browser language
- **WHEN** a guest who never chose a language, on a browser whose preferred language is French, signs up
- **THEN** the new account's preferred language is `en`

### Requirement: Account Language Wins While Signed In
While the user is authenticated and the account's preferred language is set, the active i18n locale SHALL be the account's preferred language. The language saved on this device MAY decide the tentative locale shown before the account is loaded, but SHALL NOT override the account's preferred language once it is loaded.

#### Scenario: i18n locale aligns with backend value on every authenticated render
- **WHEN** `UserService.current` is populated and `preferred_language` is set
- **THEN** `i18n.getLocale()` SHALL return that value

#### Scenario: Saved language differs from the account's language
- **WHEN** the language saved on this device is `en`
- **AND** a signed-in user whose account language is `ja` opens the app
- **THEN** the app SHALL show Japanese as soon as the account is loaded
- **AND** the language saved on this device SHALL then be `ja`
