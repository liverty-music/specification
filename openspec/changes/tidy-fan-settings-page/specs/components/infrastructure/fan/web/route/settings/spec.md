# Spec Delta

## ADDED Requirements

### Requirement: Settings sections follow a fixed order

The Settings page SHALL show its sections in this order: Account (アカウント), Name on your tickets (チケットの名義), Notifications and sound (通知とサウンド), Display and controls (表示と操作), Help improve the service (サービス改善の協力), About (このアプリについて), then the Sign Out group and the Delete account group. Notifications and sound SHALL hold Push Notifications, Sound Effects and its volume; Display and controls SHALL hold My Home Area, Language and Left-handed mode. For a guest, the sign-in hero SHALL come first and the sections that need an account (Account, Name on your tickets, Sign Out, Delete account, and the Push Notifications row) SHALL NOT be shown; the remaining sections keep the same relative order.

#### Scenario: Signed-in fan sees the account first

- **WHEN** a signed-in fan opens Settings
- **THEN** the section titles read, from top to bottom, アカウント, チケットの名義, 通知とサウンド, 表示と操作, サービス改善の協力, このアプリについて
- **AND** the Sign Out group and then the Delete account group follow About

#### Scenario: Guest sees the hero, then the preferences

- **WHEN** a guest opens Settings
- **THEN** the sign-in hero comes first, followed by 通知とサウンド (Sound Effects only), 表示と操作, サービス改善の協力 and このアプリについて
- **AND** no Account, Name on your tickets, Sign Out or Delete account section is shown

### Requirement: Each Settings row has its own icon

Two rows on the Settings page SHALL NOT show the same icon, so an icon never suggests that two different settings are the same thing. Rows of the About section stay iconless.

#### Scenario: Consent rows and Passkeys

- **WHEN** a signed-in fan views Settings
- **THEN** the two consent toggles and the Passkeys row each show an icon that no other row shows

### Requirement: Identity verification strength is stated in everyday words

When the identity verification (本人確認, identity check) row shows how strongly a verified fan is known to hold one account, it SHALL say so in everyday words, not in terms such as "dedupe". In Japanese a strong check SHALL read 「1人1アカウントを確実に確認済み」 and a weaker check 「1人1アカウントを簡易的に確認済み」.

#### Scenario: Fan verified with My Number Card

- **WHEN** a fan verified with マイナンバーカード opens Settings in Japanese
- **THEN** the identity verification row reads 「1人1アカウントを確実に確認済み」 and no row contains the word 重複排除

### Requirement: Consent toggles invite the fan to help, in plain words

The Settings page SHALL present the analytics consent toggles using labels and descriptions that name the consent *purpose* (what the data is used for) in words a fan without technical knowledge understands, and that invite the fan to help improve the service. They SHALL NOT name the data's processing *geography*, and SHALL NOT call the data anonymous, because a signed-in fan's data is tied to their account. Each consent toggle on the Settings page SHALL remain a persistent, user-controlled opt-out for the corresponding consent purpose. The Settings page SHALL NOT present a per-region ("domestic" vs "overseas") processing toggle, and SHALL NOT remove a consent purpose's Settings opt-out while that purpose can be granted at signup.

In Japanese the section and toggles SHALL read:

- Section 「サービス改善の協力」, introduced by 「Liverty Music はユーザーの皆さんと共に進化していきます。あなたの使い方が、次のアップデートを決める一番の手がかりになります。」
- Analytics: label 「利用状況を共有する」, description 「どの画面で迷ったか、どこでエラーが起きたかを知って、改善に役立てます。名前・メールアドレス・電話番号などは送りません。オフにすると、利用状況とエラーの情報を送らなくなります。」
- Session replay: label 「画面操作ログを共有する」, description 「タップやスクロールの流れを、入力内容や画面の文字を伏せて記録します。わかりにくいボタンや迷いやすい手順を見つけるために使います。オフにしても、他の設定には影響しません。」

#### Scenario: Analytics toggle is labeled by its purpose

- **WHEN** the サービス改善の協力 section is rendered
- **THEN** the product-analytics toggle SHALL be bound to the product-analytics consent purpose
- **AND** its label SHALL read 「利用状況を共有する」 in Japanese
- **AND** its description SHALL say that it is used to find where fans get lost and where errors occur, that name, email address and phone number are not sent, and what turning it off stops

#### Scenario: Session-replay toggle is labeled by its purpose

- **WHEN** the サービス改善の協力 section is rendered
- **THEN** the second toggle SHALL be bound to the `sessionReplay` consent purpose
- **AND** its label SHALL read 「画面操作ログを共有する」 in Japanese
- **AND** its description SHALL say that typed input and on-screen text are hidden in the recording, and that turning it off has no effect on other settings

#### Scenario: No anonymity claim

- **WHEN** either consent toggle's description is shown, in any language
- **THEN** it SHALL NOT describe the data as anonymous or anonymised

#### Scenario: Settings opt-out persists for a purpose granted at signup

- **WHEN** a user granted a consent purpose at the signup consent screen
- **THEN** the Settings page SHALL render a corresponding toggle that lets the user withdraw that consent
- **AND** the toggle SHALL reflect the persisted consent state on load

## MODIFIED Requirements

### Requirement: Settings exposes Analytics and Session-replay opt-out toggles
The settings page SHALL present two independent opt-out toggles under the "Help improve the service" (サービス改善の協力) section: **Analytics** (controls PostHog event capture, identification, and persistent storage) and **Session replay** (controls session recording only). Both SHALL default to on for authenticated users and SHALL be independently controllable. Each SHALL carry a plain-language description. The section SHALL carry one sentence below its toggles with an inline link to the Privacy Policy; it SHALL NOT add a Privacy Policy row of its own (the About section holds the only one).

The pre-opt-out field formerly named `marketingMeasurement` SHALL be renamed `sessionReplay`; the persisted consent-state version SHALL bump and migrate prior `v1` payloads.

#### Scenario: Both toggles default to on
- **WHEN** an authenticated user opens the settings page without having changed either toggle
- **THEN** the Analytics toggle SHALL render as on
- **AND** the Session-replay toggle SHALL render as on
- **AND** each toggle SHALL be independently controllable

#### Scenario: User disables session replay but keeps event analytics
- **WHEN** the user turns the Session-replay toggle off and leaves Analytics on
- **THEN** the application SHALL call `posthog.set_config` to stop session recording
- **AND** the application SHALL continue capturing catalogue events and SHALL keep the identified profile active

#### Scenario: One Privacy Policy link next to the toggles
- **WHEN** the サービス改善の協力 section is displayed
- **THEN** one sentence below its card links to the in-app Privacy Policy (`/legal/privacy`)
- **AND** the section contains no Privacy Policy row

---

### Requirement: About Section
The system SHALL provide access to legal and licensing information via in-app routes, and a way to contact support. The About section SHALL hold the only Privacy Policy row on the Settings page.

#### Scenario: Legal links
- **WHEN** the About section is displayed
- **THEN** the system SHALL show links to Terms of Service, Privacy Policy, and OSS Licenses
- **AND** each link SHALL target its in-app route (`/legal/terms`, `/legal/privacy`, `/legal/licenses`) rather than an external URL
- **AND** tapping a link SHALL navigate to the corresponding in-app legal document page

#### Scenario: Contact support
- **WHEN** a fan taps the お問い合わせ (Contact) row in the About section
- **THEN** the device's mail app opens a new message to the support email address

---

### Requirement: Sign Out
The system SHALL allow authenticated users to sign out of their account. The Sign Out control SHALL be rendered only when the user is authenticated and SHALL be hidden for guest (unauthenticated) users. It SHALL stand apart from every other control, in a group of its own below the About section with at least 24px between them, so a tap meant for another row never reaches it. Only the Delete account control SHALL come after it. Activating Sign Out SHALL open a modal confirmation dialog whose Cancel control receives initial focus; only confirming SHALL sign the user out, and Cancel or Escape SHALL close the dialog with the user still signed in.

#### Scenario: Sign out action
- **WHEN** an authenticated user taps the "Sign Out" button and confirms in the dialog
- **THEN** the system SHALL clear the user's authentication session
- **AND** the system SHALL navigate to the Landing Page
- **AND** the Sign Out button SHALL be visually distinct (e.g., red text) and positioned at the bottom of the settings list, above only the Delete account control

#### Scenario: Sign out asks first
- **WHEN** an authenticated user taps the "Sign Out" button
- **THEN** a modal dialog asks 「サインアウトしますか？」 and says the fan will sign in again with a passkey next time
- **AND** the dialog's Cancel control has focus

#### Scenario: Sign out cancelled
- **WHEN** the user presses Cancel or Escape in the sign-out dialog
- **THEN** the dialog closes and the user stays signed in on the Settings page

#### Scenario: Sign out apart from account rows
- **WHEN** an authenticated user views the About section with the Version row as its last row
- **THEN** the Sign Out control SHALL be in a separate group below it, at least 24px away, not adjoining the Version row

#### Scenario: Sign out hidden for guests
- **WHEN** an unauthenticated (guest) user views the Settings page
- **THEN** the system SHALL NOT render the Sign Out control

### Requirement: Guest-Adaptive Account Section

The system SHALL adapt the Settings page to authentication state. For guests, the system SHALL present the sign-in / sign-up call to action as a visually emphasized hero placed at the TOP of the Settings page (before the preferences content), and SHALL hide account-bound controls (email address, email verification status, resend-verification, sign-out). For authenticated users, the system SHALL NOT render the guest hero, and the ACCOUNT section, first on the page, SHALL present the existing account controls.

#### Scenario: Guest sees a prominent sign-in hero at the top

- **WHEN** an unauthenticated user views the Settings page
- **THEN** the system SHALL render a guest call-to-action hero at the top of the page, above the preferences content
- **AND** the hero SHALL be visually distinct from the standard list cards (e.g. brand-tinted background and a filled primary action)
- **AND** the hero SHALL offer a primary "ログイン" action and a secondary "新規登録" action that initiate the OIDC sign-in / sign-up flow
- **AND** the email address row, email-verification badge, and resend-verification button SHALL NOT be rendered

#### Scenario: Authenticated user sees account controls and no guest hero

- **WHEN** an authenticated user views the Settings page
- **THEN** the system SHALL NOT render the guest hero
- **AND** the ACCOUNT section, first on the page, SHALL render the email address, the verification badge and the resend-verification button (when unverified)
- **AND** the Sign Out control SHALL be rendered in its own group near the bottom of the page

### Requirement: Settings Page Layout and Scroll

The Settings page SHALL render a fixed page header and a vertically scrollable
content area. The settings section list SHALL scroll within the content area
without displacing or overlapping the fixed header, and the bottom navigation
bar SHALL remain unaffected. The content scroll container SHALL follow the
project's shared route scroll pattern: the content track grid item SHALL set
`min-block-size: 0` so it can shrink within its track, and scrolling SHALL be
owned by a scroll container whose minimum size does not prevent overflow.

#### Scenario: First preferences row is visible on load
- **WHEN** the Settings page loads
- **THEN** the first section (the ACCOUNT section title and its first row for a signed-in fan, the guest hero for a guest)
  SHALL be visible within the content area
- **AND** it SHALL NOT be clipped by or rendered behind the fixed page header

#### Scenario: Section list scrolls within the content area
- **WHEN** the settings content exceeds the available viewport height
- **THEN** the section list SHALL scroll vertically within the content area
- **AND** the page header SHALL remain pinned at the top
- **AND** the bottom navigation bar SHALL remain pinned at the bottom

#### Scenario: Content track item can shrink
- **WHEN** the Settings route lays out its `header` / `content` grid
- **THEN** the content-area grid item SHALL set `min-block-size: 0`
- **AND** the scroll container SHALL engage `overflow-y: auto` rather than
  expanding the grid track to full content height

### Requirement: The fan edits their name and phone number

The settings screen SHALL show the fan's saved full name and phone number as one row in the Name on your tickets (チケットの名義) section, say that they are shown on the face of the fan's tickets, and let the fan change them with UserService.Update. Tapping the row SHALL open a bottom sheet with the name and phone fields and a save action. A phone number SHALL be entered in the domestic form and sent in E.164 form. Saving a change SHALL first open a modal confirmation dialog that shows the new name and phone number and says that the tickets the fan holds will show them; Cancel SHALL receive initial focus, and only confirming SHALL call UserService.Update.

#### Scenario: Fan changes their phone number
- **WHEN** a fan with the saved phone number 090-1234-5678 opens the row, enters 090-9876-5432, saves and confirms
- **THEN** UserService.Update is called with `+819098765432`, the sheet closes and the row shows the new number

#### Scenario: Saving asks first
- **WHEN** a fan changes their name in the sheet and saves
- **THEN** a modal dialog shows the new name and phone number and says 「保有中のチケットの券面もこの名義に変わります」
- **AND** UserService.Update has not been called yet

#### Scenario: Fan cancels the confirmation
- **WHEN** the fan presses Cancel or Escape in that dialog
- **THEN** UserService.Update is not called and the sheet stays open with the fan's input

#### Scenario: No details saved yet
- **WHEN** a fan who never gave a name or phone number opens the settings screen
- **THEN** the row says that no name is saved, and tapping it opens the sheet with both fields empty and ready to fill in

## REMOVED Requirements

### Requirement: Privacy & Analytics Consent Toggle Labeling

**Reason**: Replaced by "Consent toggles invite the fan to help, in plain words". The old requirement described the data as anonymous, which is not true for a signed-in fan whose analytics are tied to their account, and one scenario still bound the second toggle to `marketingMeasurement`, a purpose renamed `sessionReplay` (see "Settings exposes Analytics and Session-replay opt-out toggles").
**Migration**: The purpose-not-geography rule, the ban on a per-region toggle and the persistent opt-out carry over unchanged into the new requirement; only the wording rules and the second toggle's purpose change.
