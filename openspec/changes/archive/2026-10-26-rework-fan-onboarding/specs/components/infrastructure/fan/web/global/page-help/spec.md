## MODIFIED Requirements

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
