# Delta for page-help

## MODIFIED Requirements

### Requirement: Persistent Help Icon in Onboarding Pages

The system SHALL make page-specific help reachable at all times on the Discovery,
Timetable, and My Artists pages, for all users regardless of onboarding state, via a
help item in the action menu (see the `fab-action-launcher` capability). The
page header SHALL NOT host a separate `?` help trigger button; help is contributed as
a launcher item on these pages. Help SHALL open only when the fan chooses that
item; it SHALL never open on its own. Guide moments (the guide-moment surface)
point fans to features instead.

#### Scenario: Help icon is always visible

- **WHEN** the user is on the Discovery, Timetable, or My Artists page
- **THEN** a help item SHALL be present in the action menu
- **AND** the item SHALL render an icon together with a text label ("ヘルプ")
- **AND** activating it SHALL open that page's help bottom-sheet

#### Scenario: No `?` trigger in the page header

- **WHEN** the Discovery, Timetable, or My Artists page header is rendered
- **THEN** the header SHALL NOT contain a `?` help trigger button
- **AND** help SHALL be reachable via the action menu

#### Scenario: Help never opens on its own

- **WHEN** a guest in onboarding opens Discovery or My Artists for the first time
- **THEN** the help bottom-sheet does not open until the guest chooses the help item

#### Scenario: Pages without page-specific help contribute no help item

- **WHEN** the user is on a page that has no page-specific help content (e.g. settings)
- **THEN** no help item SHALL be contributed to the launcher for that page

### Requirement: Page-specific Help Content

The help bottom-sheet SHALL display page-specific guide content when opened. Only the active page's content SHALL be rendered. Each page's content SHALL be composed of one or more discrete sub-sections (see "Multi-section help sheet structure"), so the sheet can address multiple topics without conflating them. Help text SHALL describe the controls the page shows today. A section whose feature has a guide moment SHALL end with a 「チュートリアル」 button that replays that moment, as the guide-moment surface's "Help replays a guide moment" states.

#### Scenario: Discovery help content

- **WHEN** the help bottom-sheet opens on the Discovery page for a signed-in fan
- **THEN** the sheet renders three sub-sections:
  - "アーティストの探し方" / "Finding Artists" — containing the description that tapping artist bubbles follows them, the inline chip demo, the two tips (genre tabs, search bar), and the 「チュートリアル」 button that replays the bubble field's guide moment
  - "ライブ" / "Concerts" — for a signed-in fan only — containing the description that the swap tile beside the orb opens the concerts near the chosen area within a chosen period, including artists the fan does not follow yet, and that an artist can be followed from a concert's detail, and the 「チュートリアル」 button that replays the swap tile's guide moment on the artist bubbles or the Concerts view's guide moment on the Concerts view
  - "フォロー解除" / "Unfollowing" — containing the single sentence pointing users to the My Artists page for unfollow operations
- **WHEN** the help bottom-sheet opens on the Discovery page for a guest
- **THEN** the sheet renders "アーティストの探し方" and "フォロー解除" and no "ライブ" section

#### Scenario: Timetable help content

- **WHEN** the help bottom-sheet opens on the Timetable page
- **THEN** the sheet renders two sub-sections:
  - "ステージレーンの読み方" / "Reading the Stage Lanes" — containing the description that followed artists' concerts are shown by distance, and the explanation list of the three stage lanes: HOME, NEAR, and AWAY
  - "ライブ詳細を見る" / "Viewing Concert Details" — containing the tip that tapping a concert card opens the concert detail
- **AND** the HOME, NEAR and AWAY labels use the home, near and away stage colors

#### Scenario: My Artists help content

- **WHEN** the help bottom-sheet opens on the My Artists page
- **THEN** the sheet renders two sub-sections, on every device:
  - "Hype（熱量） について" / "About Hype" — containing:
    - The description sentence: JA `Hype（熱量）で通知の範囲が変わります。` / EN `Hype controls how far away you get notified.` (the dots on each row explain themselves; the help does not describe them)
    - The tier table (see "Hype tier table is a 3-column grid") explaining the four hype tier values: `Watch / 通知なし` · `Home / HOMEエリアのライブを通知` · `Nearby / 近くのライブも通知` · `Away / 全てのライブを通知`
    - A practical tip: JA `遠征してでも見たいアーティストは Away に設定してみましょう！` / EN `Set artists you'd travel for to Away to never miss them!`
    - The 「チュートリアル」 button that replays the hype dots' guide moment
  - "フォロー解除" / "Unfollowing" — containing: JA `画面下中央のアクションメニューで「編集」を選ぶと、各行に削除ボタンが表示され、フォローを解除できます。` / EN `Choose Edit in the action menu at the bottom centre to show a remove button on each row and unfollow artists.`
- **AND** the help text does not mention a slider, a header Edit control, a long-press gesture, or a menu at the bottom right (the action menu is centred in the bottom navigation bar)

#### Scenario: Replay from Discovery help

- **WHEN** a fan who follows 10 artists opens Discovery help on the artist bubbles and presses 「チュートリアル」 in "アーティストの探し方"
- **THEN** help closes and the bubble field's guide moment appears

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
  - `🔥` · `Home` · "HOMEエリアのライブを通知" (JA) / "Notify for home-area concerts" (EN)
  - `🔥🔥` · `Nearby` · "近くのライブも通知" (JA) / "Notify for nearby concerts too" (EN)
  - `🔥🔥🔥` · `Away` · "全てのライブを通知" (JA) / "Notify for every concert" (EN)
- **AND** the tier labels in column 2 are the invariant English forms regardless of locale
- **AND** the Away description does not contain the word `全国`

#### Scenario: Semantic markup

- **WHEN** a screen reader reads the hype tier grid
- **THEN** it reads a list of four items, each item giving the tier label and its description
- **AND** it does not read the decorative tier icons

### Requirement: Help seen flags cleared on onboarding reset

The system SHALL clear the per-level flags that record which hype snacks My Artists has shown when the guest's local data is reset, at sign-in and when sign-up completes, so that each hype snack appears again for the next session. Tapping [Get Started] on Welcome SHALL NOT clear them. The record of seen guide moments SHALL NOT be cleared then (guide-moment surface, "Each guide moment is shown once per device and survives sign-up").

#### Scenario: Help-seen flags cleared on fresh onboarding

- **WHEN** the guest's local data is reset at sign-in or when sign-up completes
- **THEN** the system SHALL clear the flags that record which hype snacks were shown
- **AND** tapping [Get Started] on Welcome SHALL NOT clear them

#### Scenario: Hype snack flags cleared at sign-up

- **WHEN** a guest who saw the hype snack for Away completes sign-up and then sets an artist to Away
- **THEN** the hype snack for Away appears again

#### Scenario: Seen guide moments are kept at sign-up

- **WHEN** a guest who saw the hype dots' guide moment completes sign-up and opens My Artists
- **THEN** the hype dots' guide moment does not appear again

## REMOVED Requirements

### Requirement: Auto-open on First Page Visit

**Reason**: Few fans read help that opens on its own, and it covers the screen at the moment the fan arrives to act. The guide moments show one feature at the moment it is needed instead.

**Migration**: Help stays reachable from the help item of the action menu on Discovery, the Timetable and My Artists. The devices' `onboarding.helpSeen:*` values are no longer read and can be left in place.
