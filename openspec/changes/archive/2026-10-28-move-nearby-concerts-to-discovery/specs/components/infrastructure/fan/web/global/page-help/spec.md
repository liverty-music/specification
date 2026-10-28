## MODIFIED Requirements

### Requirement: Page-specific Help Content

The help bottom-sheet SHALL display page-specific guide content when opened. Only the active page's content SHALL be rendered. Each page's content SHALL be composed of one or more discrete sub-sections (see "Multi-section help sheet structure"), so the sheet can address multiple topics without conflating them. Help text SHALL describe the controls the page shows today.

#### Scenario: Discovery help content

- **WHEN** the help bottom-sheet opens on the Discovery page
- **THEN** the sheet renders three sub-sections:
  - "アーティストの探し方" / "Finding Artists" — containing the description that tapping artist bubbles follows them, the inline chip demo, and the two tips (genre tabs, search bar)
  - "近くのライブ" / "Near you" — containing the description that the swap tile beside the orb opens the concerts near the chosen area within a chosen period, including artists the fan does not follow yet, and that an artist can be followed from a concert's detail
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
