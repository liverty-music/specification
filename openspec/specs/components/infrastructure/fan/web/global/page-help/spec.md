# Page Help

## Purpose

Provides persistent, page-specific help content via a help icon and bottom-sheet on the Discovery, Dashboard, and My Artists pages. Auto-opens on first visit to each page during onboarding to deliver contextual guidance without blocking the user's flow. The help icon remains accessible after onboarding completes so users can revisit guidance at any time.

## Requirements

### Requirement: Persistent Help Icon in Onboarding Pages

The system SHALL make page-specific help reachable at all times on the Discovery,
Dashboard, and My Artists pages, for all users regardless of onboarding state, via a
help item in the FAB action launcher (see the `fab-action-launcher` capability). The
page header SHALL NOT host a separate `?` help trigger button; help is contributed as
a launcher item on these pages. Auto-open on first visit (defined by the
"Auto-open on First Page Visit" requirement) opens the same help bottom-sheet
directly and does not depend on the presence of a header trigger.

#### Scenario: Help icon is always visible

- **WHEN** the user is on the Discovery, Dashboard, or My Artists page
- **THEN** a help item SHALL be present in the FAB action launcher
- **AND** the item SHALL render an icon together with a text label ("ヘルプ")
- **AND** activating it SHALL open that page's help bottom-sheet

#### Scenario: No `?` trigger in the page header

- **WHEN** the Discovery, Dashboard, or My Artists page header is rendered
- **THEN** the header SHALL NOT contain a `?` help trigger button
- **AND** help SHALL be reachable via the FAB action launcher

#### Scenario: Pages without page-specific help contribute no help item

- **WHEN** the user is on a page that has no page-specific help content (e.g. settings)
- **THEN** no help item SHALL be contributed to the launcher for that page

### Requirement: Auto-open on First Page Visit

The system SHALL automatically open the help bottom-sheet on the user's first visit to the Discovery page and to the My Artists page while the user is onboarding. The Dashboard help SHALL never open on its own. Each page's help SHALL auto-open at most once until the guest's local data is reset (see "Help seen flags cleared on onboarding reset").

#### Scenario: First visit to Discovery during onboarding

- **WHEN** the user arrives at the Discovery page for the first time while onboarding
- **THEN** the Discovery help bottom-sheet opens automatically

#### Scenario: First visit to My Artists during onboarding

- **WHEN** the user arrives at the My Artists page for the first time while onboarding
- **THEN** the My Artists help bottom-sheet opens automatically

#### Scenario: Subsequent visits do not auto-open

- **WHEN** the user visits a page whose help has already auto-opened
- **THEN** the help bottom-sheet does not open automatically
- **AND** the user can open it from the help item of the FAB action launcher

#### Scenario: No auto-open after onboarding

- **WHEN** a user whose onboarding is completed visits Discovery or My Artists for the first time
- **THEN** the help bottom-sheet does not open automatically

#### Scenario: Dashboard help never auto-opens

- **WHEN** the user arrives at the Dashboard for the first time while onboarding
- **THEN** the Dashboard help bottom-sheet does not open automatically

### Requirement: Page-specific Help Content

The help bottom-sheet SHALL display page-specific guide content when opened. Only the active page's content SHALL be rendered. Each page's content SHALL be composed of one or more discrete sub-sections (see "Multi-section help sheet structure"), so the sheet can address multiple topics without conflating them. Help text SHALL describe the controls the page shows today.

#### Scenario: Discovery help content

- **WHEN** the help bottom-sheet opens on the Discovery page
- **THEN** the sheet renders two sub-sections:
  - "アーティストの探し方" / "Finding Artists" — containing the description that tapping artist bubbles follows them, the inline chip demo, and the two tips (genre tabs, search bar)
  - "フォロー解除" / "Unfollowing" — containing the single sentence pointing users to the My Artists page for unfollow operations

#### Scenario: Dashboard help content

- **WHEN** the help bottom-sheet opens on the Dashboard page
- **THEN** the sheet renders two sub-sections:
  - "ステージレーンの読み方" / "Reading the Stage Lanes" — containing the description that followed artists' concerts are shown by distance, and the explanation list of the three stage lanes: HOME, NEAR, and AWAY
  - "ライブ詳細を見る" / "Viewing Concert Details" — containing the tip that tapping a concert card opens the concert detail
- **AND** the HOME, NEAR and AWAY labels use the home, near and away stage colors

#### Scenario: My Artists help content

- **WHEN** the help bottom-sheet opens on the My Artists page
- **THEN** the sheet renders two sub-sections, on every device:
  - "Hype（熱量） について" / "About Hype" — containing:
    - The description sentence: JA `Hype（熱量）で通知の範囲が変わります。` / EN `Hype controls how far away you get notified.` (the dots on each row explain themselves; the help does not describe them)
    - The tier table (see "Hype tier table is a 3-column grid") explaining the four hype tier values: `Watch / 通知なし` · `Home / 居住エリアのライブを通知` · `Nearby / 近くのライブも通知` · `Away / 全てのライブを通知`
    - A practical tip: JA `遠征してでも見たいアーティストは Away に設定してみましょう！` / EN `Set artists you'd travel for to Away to never miss them!`
  - "フォロー解除" / "Unfollowing" — containing: JA `画面下中央のアクションメニューで「編集」を選ぶと、各行に削除ボタンが表示され、フォローを解除できます。` / EN `Choose Edit in the action menu at the bottom centre to show a remove button on each row and unfollow artists.`
- **AND** the help text does not mention a slider, a header Edit control, a long-press gesture, or a menu at the bottom right (the action menu is centred in the bottom navigation bar)

### Requirement: Multi-section help sheet structure

Each page-help sheet (Discovery, Dashboard, My Artists) SHALL be composed of one or more `<section>` blocks, each prefixed by a section-title row consisting of an info icon and a heading. The bottom-sheet itself SHALL carry the accessible name via its `aria-label`; the sheet SHALL NOT use a single per-sheet top-level `<h2>` heading.

#### Scenario: Section title structure

- **WHEN** the help sheet renders for any of the three pages
- **THEN** each sub-section SHALL begin with a `<header>` row containing:
  - An icon (`<svg-icon name="info">` or equivalent visual marker)
  - A heading element of level `<h3>` with CSS class `help-section-title`
  - A bottom border (visual divider) separating the heading from the section body
- **AND** the heading element SHALL be the section's accessible name (no separate `aria-labelledby` indirection needed if the heading is the direct child of the section)

#### Scenario: No sheet-level heading

- **WHEN** the help sheet renders
- **THEN** the sheet SHALL NOT contain an `<h2>` heading representing the sheet as a whole
- **AND** the sheet's accessible name SHALL be provided exclusively by the bottom-sheet's `aria-label` attribute
- **AND** the legacy `.page-help-title` CSS class SHALL NOT appear in the rendered DOM

#### Scenario: Multiple sub-sections render in document order

- **WHEN** a help sheet contains more than one sub-section
- **THEN** the sub-sections SHALL render in document order (top-to-bottom)
- **AND** each sub-section's section-title row SHALL maintain visual consistency with the others (same icon size, same heading typography, same divider treatment)

### Requirement: Hype tier table is a 3-column grid

The My Artists help sheet's hype tier explanation SHALL render as a list of four rows laid out on one shared 3-column grid, where:
- Column 1 is sized to its widest cell and contains the tier icon (`👀`, `🔥`, `🔥🔥`, `🔥🔥🔥`), centered and hidden from assistive technology.
- Column 2 is sized to its widest cell and contains the invariant English tier label (`Watch`, `Home`, `Nearby`, `Away`), start-aligned.
- Column 3 takes the remaining width and contains the notification-scope description sentence, start-aligned.

#### Scenario: Column alignment

- **WHEN** the My Artists help sheet renders the hype tier explanation
- **THEN** the four rows share three vertical column edges (icon-column right edge, label-column right edge, description-column left edge are each aligned across all rows)
- **AND** the label-column left edge is aligned across all four rows regardless of icon width (`👀` is narrower than `🔥🔥🔥`)
- **AND** the description-column left edge is aligned across all four rows regardless of label width (`Home` is narrower than `Nearby`)

#### Scenario: Tier content per row

- **WHEN** the help sheet renders the hype tier grid
- **THEN** the four rows are (in order, top-to-bottom):
  - `👀` · `Watch` · "通知なし" (JA) / "No notifications" (EN)
  - `🔥` · `Home` · "居住エリアのライブを通知" (JA) / "Notify for home-area concerts" (EN)
  - `🔥🔥` · `Nearby` · "近くのライブも通知" (JA) / "Notify for nearby concerts too" (EN)
  - `🔥🔥🔥` · `Away` · "全てのライブを通知" (JA) / "Notify for every concert" (EN)
- **AND** the tier labels in column 2 are the invariant English forms regardless of locale
- **AND** the Away description does not contain the word `全国`

#### Scenario: Semantic markup

- **WHEN** a screen reader reads the hype tier grid
- **THEN** it reads a list of four items, each item giving the tier label and its description
- **AND** it does not read the decorative tier icons

### Requirement: Help sheet visual readability

The help bottom-sheet SHALL use design tokens that ensure clear visual distinction from the app surface.

#### Scenario: Sheet background, title font, and muted text rendering

- **WHEN** the help bottom-sheet is displayed
- **THEN** the sheet background SHALL use `var(--color-surface-overlay)` so the sheet is visually elevated above the page surface
- **AND** help section titles SHALL use `font-family: var(--font-display)`
- **AND** secondary text (notes, tips) SHALL use `color: var(--color-text-secondary)` instead of reduced opacity

### Requirement: Help seen flags cleared on onboarding reset

The system SHALL clear all per-page help-seen flags when the guest's local data is reset, at sign-in and when sign-up completes, so that contextual help auto-opens again for the next session. Tapping [Get Started] on Welcome SHALL NOT clear them.

#### Scenario: Help-seen flags cleared on fresh onboarding

- **WHEN** the guest's local data is reset at sign-in or when sign-up completes
- **THEN** the system SHALL clear all `onboarding.helpSeen:*` keys from localStorage
- **AND** tapping [Get Started] on Welcome SHALL NOT clear them
