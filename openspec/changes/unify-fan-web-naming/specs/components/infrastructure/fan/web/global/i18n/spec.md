# Spec Delta

## MODIFIED Requirements

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
  - `Screen title — Concert` — JA: `Concert` / EN: `Concert` (key `nav.concert`)
  - `Screen title — Notifications` — JA: `Notifications` / EN: `Notifications` (key `nav.notifications`)
  - `Screen title — Passkeys` — JA: `Passkeys` / EN: `Passkeys` (key `nav.passkeys`)
  - `Screen title — Delete Account` — JA: `Delete Account` / EN: `Delete Account` (key `nav.deleteAccount`)
  - `Screen title — Order Detail` — JA: `Order Detail` / EN: `Order Detail` (key `nav.order`)
  - `Screen title — Checkout` — JA: `Checkout` / EN: `Checkout` (key `nav.checkout`)
  - `Screen title — Lottery Entry` — JA: `Lottery Entry` / EN: `Lottery Entry` (key `nav.newLotteryEntry`)
  - `Screen title — Lottery Entries` — JA: `Lottery Entries` / EN: `Lottery Entries` (key `nav.lotteryEntries`)
  - `Screen title — Resale Entry` — JA: `Resale Entry` / EN: `Resale Entry` (key `nav.newResaleEntry`)
  - `Screen title — Resale Entries` — JA: `Resale Entries` / EN: `Resale Entries` (key `nav.resaleEntries`)
  - `Screen title — Can't Sign In` — JA: `Can't Sign In` / EN: `Can't Sign In` (key `nav.signInHelp`)
  - `Screen title — Verify Email` — JA: `Verify Email` / EN: `Verify Email` (key `nav.verifyEmail`)
  - `Screen title — Welcome` — JA: `Welcome` / EN: `Welcome` (key `nav.welcome`)
  - `Screen title — About` — JA: `About` / EN: `About` (key `nav.about`)
  - `Screen title — Privacy & Analytics` — JA: `Privacy & Analytics` / EN: `Privacy & Analytics` (key `nav.consent`)
  - `Screen title — Terms of Service` — JA: `Terms of Service` / EN: `Terms of Service` (key `nav.legalTerms`)
  - `Screen title — Privacy Policy` — JA: `Privacy Policy` / EN: `Privacy Policy` (key `nav.legalPrivacy`)
  - `Screen title — OSS Licenses` — JA: `OSS Licenses` / EN: `OSS Licenses` (key `nav.legalLicenses`)
  - `Screen title — Signing In` — JA: `Signing In` / EN: `Signing In` (key `nav.signInCallback`)
  - `Screen title — Identity Verification` — JA: `Identity Verification` / EN: `Identity Verification` (key `nav.identityVerificationCallback`)
  - `Screen title — Passkeys` — JA: `Passkeys` / EN: `Passkeys` (key `nav.passkeysCallback`)
  - `Screen title — Page Not Found` — JA: `Page Not Found` / EN: `Page Not Found` (key `nav.notFound`)
  - `Personal timetable promise` — JA: `あなただけのタイムテーブル` / EN: `your personal timetable`
  - `HOME lane` — JA: `HOME` / EN: `HOME` (the timetable's stage header and the help sheet's lane legend; a lane is "the HOME lane" in prose)
  - `NEAR lane` — JA: `NEAR` / EN: `NEAR`
  - `AWAY lane` — JA: `AWAY` / EN: `AWAY`
  - `Hype concept label` — JA: `Hype` / EN: `Hype`
  - `Hype tier — Watch` — JA: `Watch` / EN: `Watch`
  - `Hype tier — Home` — JA: `Home` / EN: `Home`
  - `Hype tier — Nearby` — JA: `Nearby` / EN: `Nearby`
  - `Hype tier — Away` — JA: `Away` / EN: `Away`

#### Scenario: Navigation tab labels are invariant across locales
- **WHEN** a navigation tab label is rendered in any UI surface (bottom navigation bar or a route's page header)
- **THEN** the label SHALL be the invariant English form from the registry, identical in JA and EN locales
- **AND** a route's page header SHALL bind the shared `nav.*` label rather than a separate localized title key

#### Scenario: Screen titles are invariant across locales
- **WHEN** a screen's title is rendered in its page header or its browser tab
- **THEN** the title SHALL be the invariant English form from the registry (a navigation tab label or a screen title), identical in JA and EN locales, bound through its `nav.*` key

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
