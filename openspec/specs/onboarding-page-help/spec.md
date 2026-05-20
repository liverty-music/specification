# Onboarding Page Help

## Purpose

Provides persistent, page-specific help content via a help icon and bottom-sheet on the Discovery, Dashboard, and My Artists pages. Auto-opens on first visit to each page during onboarding to deliver contextual guidance without blocking the user's flow. The help icon remains accessible after onboarding completes so users can revisit guidance at any time.

## Requirements

### Requirement: Persistent Help Icon in Onboarding Pages

The system SHALL display a persistent `?` help icon in the top-right area of the Discovery, Dashboard, and My Artists pages for all users regardless of onboarding state.

#### Scenario: Help icon is always visible

- **WHEN** the user is on the Discovery, Dashboard, or My Artists page
- **THEN** a `?` icon button SHALL be visible in the top-right corner of the page header
- **AND** the button SHALL have `aria-label="ヘルプを表示"` for accessibility

### Requirement: Auto-open on First Page Visit

The system SHALL automatically open the help bottom-sheet on the user's first visit to each page during onboarding.

#### Scenario: First visit to Discovery during onboarding

- **WHEN** the user arrives at the Discovery page for the first time during onboarding
- **AND** `localStorage['liverty:onboarding:helpSeen:discovery']` is not set
- **THEN** the help bottom-sheet SHALL open automatically
- **AND** the system SHALL set `localStorage['liverty:onboarding:helpSeen:discovery']` to `'1'`

#### Scenario: First visit to My Artists during onboarding

- **WHEN** the user arrives at the My Artists page for the first time during onboarding
- **AND** `localStorage['liverty:onboarding:helpSeen:my-artists']` is not set
- **THEN** the help bottom-sheet SHALL open automatically
- **AND** the system SHALL set `localStorage['liverty:onboarding:helpSeen:my-artists']` to `'1'`

#### Scenario: Subsequent visits do not auto-open

- **WHEN** the user visits a page where `localStorage['liverty:onboarding:helpSeen:<page>']` is already set
- **THEN** the help bottom-sheet SHALL NOT open automatically
- **AND** the user MAY open it manually by tapping the `?` icon

### Requirement: Page-specific Help Content

The help bottom-sheet SHALL display page-specific guide content when opened. Only the active page's content SHALL be rendered (mutually exclusive, enforced via `switch.bind` on the `page` bindable). Each page's content SHALL be composed of one or more discrete sub-sections (see "Multi-section help sheet structure"), so the sheet can address multiple topics without conflating them.

#### Scenario: Discovery help content

- **WHEN** the help bottom-sheet opens on the Discovery page
- **THEN** the sheet SHALL render two sub-sections:
  - `pageHelp.discovery.findingSectionTitle` ("アーティストの探し方" / "Finding Artists") — containing the description that tapping artist bubbles follows them, the inline chip demo, and the two tips (genre tabs, search bar)
  - `pageHelp.discovery.unfollowSectionTitle` ("フォロー解除" / "Unfollowing") — containing the single sentence pointing users to the My Artists page for unfollow operations

#### Scenario: Dashboard help content

- **WHEN** the help bottom-sheet opens on the Dashboard page
- **THEN** the sheet SHALL render two sub-sections:
  - `pageHelp.dashboard.lanesSectionTitle` ("ステージレーンの読み方" / "Reading the Stage Lanes") — containing the description that followed artists' concerts are shown by distance, and the explanation list of the three stage lanes: HOME, NEAR, and AWAY
  - `pageHelp.dashboard.detailsSectionTitle` ("ライブ詳細を見る" / "Viewing Concert Details") — containing the tip that tapping a concert card opens the concert detail
- **AND** the HOME stage label SHALL use `color: var(--color-stage-home)` via the `.stage-home` CSS class
- **AND** the NEAR stage label SHALL use `color: var(--color-stage-near)` via the `.stage-near` CSS class
- **AND** the AWAY stage label SHALL use `color: var(--color-stage-away)` via the `.stage-away` CSS class
- **AND** stage labels SHALL NOT use `data-stage` attributes (reserved for `concert-highway` lane headers)

#### Scenario: My Artists help content

- **WHEN** the help bottom-sheet opens on the My Artists page
- **THEN** the sheet SHALL render one or two sub-sections:
  - `pageHelp.myArtists.hypeSectionTitle` ("Hype（熱量） について" / "About Hype") — containing:
    - The description sentence: JA `Hype（熱量） で通知の範囲が変わります。スライダーをタップして切り替えられます。` / EN `Hype controls how far away you get notified. Tap the slider to change it.`
    - A 3-column tier table (see "Hype tier table is a 3-column grid") explaining the four hype tier values: `Watch / 通知なし` · `Home / 居住エリアのライブを通知` · `Nearby / 近くのライブも通知` · `Away / 全てのライブを通知`
    - A practical tip: JA `遠征してでも見たいアーティストは Away に設定してみましょう！` / EN `Set artists you'd travel for to Away to never miss them!`
  - `pageHelp.myArtists.unfollowSectionTitle` ("フォロー解除" / "Unfollowing") — containing the long-press tip; this sub-section SHALL be rendered ONLY when the device is pointer-coarse (touch device), guarded by `if.bind="isPointerCoarse"` at the `<section>` element

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

The My Artists help sheet's hype tier explanation SHALL render as a 3-column CSS Grid (or semantically-equivalent `<dl>` with grid layout), where:
- Column 1 is `auto` width and contains the tier icon (`👀`, `🔥`, `🔥🔥`, `🔥🔥🔥`), centered.
- Column 2 is `auto` width and contains the invariant English tier label (`Watch`, `Home`, `Nearby`, `Away`), start-aligned.
- Column 3 is `1fr` width and contains the notification-scope description sentence, start-aligned.

#### Scenario: Column alignment

- **WHEN** the My Artists help sheet renders the hype tier explanation
- **THEN** the four rows SHALL share three vertical column edges (icon-column right edge, label-column right edge, description-column left edge are each aligned across all rows)
- **AND** the label-column left edge SHALL be aligned across all four rows regardless of icon width (`👀` is narrower than `🔥🔥🔥`)
- **AND** the description-column left edge SHALL be aligned across all four rows regardless of label width (`Home` is narrower than `Nearby`)

#### Scenario: Tier content per row

- **WHEN** the help sheet renders the hype tier grid
- **THEN** the four rows SHALL be (in order, top-to-bottom):
  - `👀` · `Watch` · "通知なし" (JA) / "No notifications" (EN)
  - `🔥` · `Home` · "居住エリアのライブを通知" (JA) / "Notify for home-area concerts" (EN)
  - `🔥🔥` · `Nearby` · "近くのライブも通知" (JA) / "Notify for nearby concerts too" (EN)
  - `🔥🔥🔥` · `Away` · "全てのライブを通知" (JA) / "Notify for every concert" (EN)
- **AND** the tier labels in column 2 SHALL be the invariant English forms regardless of locale (per the `Hype Tier Surface Labels Are Layer B` requirement in the `brand-vocabulary` capability)
- **AND** the Away description SHALL NOT contain the word `全国` (the old JA copy was inaccurate because the proto's `HYPE_TYPE_AWAY` semantics include international concerts, not only nationwide)

#### Scenario: Semantic markup

- **WHEN** the help sheet renders the hype tier grid
- **THEN** the grid SHALL use a semantic `<dl>` (definition list) where each tier is encoded as a pair of `<dt>` elements (icon + label) followed by a single `<dd>` element (description)
- **AND** the template SHALL carry an inline implementation comment noting the two-`<dt>`-per-`<dd>` pattern so future contributors understand why the icon and label are NOT merged into one element

### Requirement: Help sheet visual readability

The help bottom-sheet SHALL use design tokens that ensure clear visual distinction from the app surface.

#### Scenario: Sheet background, title font, and muted text rendering

- **WHEN** the help bottom-sheet is displayed
- **THEN** the sheet background SHALL use `var(--color-surface-overlay)` so the sheet is visually elevated above the page surface
- **AND** help section titles SHALL use `font-family: var(--font-display)`
- **AND** secondary text (notes, tips) SHALL use `color: var(--color-text-secondary)` instead of reduced opacity

### Requirement: Top-layer Popover Text Color Inheritance

All popover and dialog elements promoted to the browser's top-layer SHALL inherit the application's text color. The global CSS layer SHALL set `color: var(--color-text-primary)` on `:where([popover], dialog)` to prevent top-layer elements from inheriting the browser-default `color: black` from `<html>`.

#### Scenario: Bottom-sheet text is readable on dark background

- **WHEN** a `bottom-sheet` component opens as a popover in the top-layer
- **THEN** all text inside the bottom-sheet SHALL inherit `color: var(--color-text-primary)` (near-white)
- **AND** the text SHALL be readable against the dark sheet background (`var(--color-surface-overlay)`)

#### Scenario: Global rule uses zero specificity

- **WHEN** the global CSS sets `color` on popover/dialog elements
- **THEN** the rule SHALL use `:where()` pseudo-class for zero specificity
- **AND** any block-level CSS rule SHALL be able to override the color without specificity conflicts

### Requirement: Help seen flags cleared on onboarding reset

- **WHEN** the user starts a fresh onboarding session (taps [Get Started] on Welcome)
- **THEN** the system SHALL clear all `liverty:onboarding:helpSeen:*` keys from localStorage
