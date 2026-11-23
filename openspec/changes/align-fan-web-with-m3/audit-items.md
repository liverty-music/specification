# Audit items behind this change

Source: fan web (frontend `main` 3e0cc066) compared with the Material 3 guideline snapshot, static code reading only. Each row is one finding; `ref` is `<unit>#<n>`. Rows are grouped by theme. Only themes this change acts on are listed (adopt, measure, and the decisions that were settled).

## T1 読み込み中を skeleton にし、内容は fade-in で出す (22)

| ref | spec | finding |
|---|---|---|
| view-transitions#n2 | spec-silent | 通知の読み込み中に、スケルトンの仮の枠がない。一行のテキストから一覧へ、高さも位置も変わって一度に切り替わる。 |
| progress-and-loading#n4 | spec-silent | The placeholder motion is a horizontal sweep of a light band (1.6s, infinite), not a subtle tone pulse that travels from the top left to the bottom right. |
| progress-and-loading#n6 | spec-silent | This component removes the skeleton and shows the slotted content in one frame. The consumer's content (the loaded list) gets no fade-in from here. The route files that slot content were not readable, so whether they add the fade-in class is unverified. |
| concert-sheet-and-cover#n3 | spec-silent | While the concert page loads, the fan sees one line of text and no skeleton placeholders in the layout of the cover, title and details. |
| concert-sheet-and-cover#n4 | spec-silent | The cover image appears at full opacity in one step after the grey box, with no fade-in. |
| concert-sheet-and-cover#n5 | spec-silent | The hero box at the top of the sheet is blank until the artist image loads, and the image then appears at full opacity in one step, with no placeholder or fade-in. |
| timetable#n8 | spec-silent | Loaded content replaces the placeholders in one frame; there is no fade over the skeleton, and the date headers never fade in. |
| timetable#n9 | spec-silent | The placeholder shimmer sweeps horizontally across each block, not diagonally from the top-left corner to the bottom-right. |
| my-artists#n9 | spec-silent | The skeleton rows are replaced by the artist table in a single frame, with no fade-in. |
| tickets-and-virtual-ticket#n21 | spec-silent | Loading shows a sentence and no skeleton, so the whole ticket list appears in one step. |
| tickets-and-virtual-ticket#n22 | spec-silent | The WebGL art replaces the flat cover in one step, with no fade. |
| purchase-and-form-flows#n3 | spec-silent | Loading states for the checkout, order and entry screens show only a line of text while the data loads. The guideline calls for a loading indicator for waits of this length. |
| purchase-and-form-flows#n4 | spec-silent | Content appears all at once after a text-only loading state, with no skeleton that holds the layout in place. |
| welcome-onboarding-celebration#n10 | spec-silent | When preview data arrives, the buttons under the hero text are replaced in one frame, with no placeholder and no fade. The CTA group shows at once, so this is a content swap rather than a blank loading state. |
| accessibility-and-reduced-motion#n4 | spec-silent | The loading motion is a sweeping highlight band, not the subtle pulse the guideline describes, and it does not move diagonally from top-left to bottom-right. |
| passkeys-and-entry-routes#n1 | spec-silent | The passkey list load (a network read that takes longer than 200 ms) shows a text line only, not a loading indicator. |
| passkeys-and-entry-routes#n2 | spec-silent | The return leg of passkey management (a code exchange and session check) shows text only during the wait. |
| passkeys-and-entry-routes#n3 | spec-silent | The lottery entry status load shows a text line only, no indicator. |
| passkeys-and-entry-routes#n4 | spec-silent | The resale entries load can take several requests (entries, then each concert), and shows text only, no indicator. |
| passkeys-and-entry-routes#n7 | spec-silent | The passkey rows appear all at once with no placeholder and no fade, so the layout jumps from a text line to a full card. |
| passkeys-and-entry-routes#n8 | spec-silent | The resale entry cards pop in at once after a text-only wait, with no placeholder and no fade. |
| passkeys-and-entry-routes#n9 | spec-silent | The entry result card appears instantly after the loading text, with no placeholder and no fade-in. |

## T2 階層を進む・戻る画面遷移（forward / backward） (4)

| ref | spec | finding |
|---|---|---|
| view-transitions#n0 | spec-requires-current-behavior | ベル（通知センター）と FAB メニューの設定は、タブの下にある一段深い画面だが、どちらも遷移の動きがない（none）。画面が一度に切り替わる。タブ切り替えの root クロスフェードとも、前後の画面の関係を示す forward/backward とも違う。 |
| view-transitions#n1 | spec-requires-current-behavior | 通知一覧の行から、通知のリンク先の画面へ進むときに移動がない（none）。階層が一段深くなるのに、戻る方向の動きもない。 |
| discovery-chrome#n3 | spec-silent | Drilling from a region into its prefectures, and back, changes the sheet content with a jump cut and no directional motion. |
| accessibility-and-reduced-motion#n5 | spec-requires-current-behavior | Moving between levels of a page hierarchy (a list to a detail, and back) has no horizontal motion, only a cross-fade. The guideline's default forward and backward pattern slides horizontally (Android's default fades as the screens slide). This is the only rout |

## T3 タブ切替を「素早く消してから出す」top level に（spec 変更あり） (5)

| ref | spec | finding |
|---|---|---|
| view-transitions#0 | spec-requires-current-behavior | タブ切り替えで旧画面の退場と新画面の登場が重なって再生される。ガイドラインは退場を素早く終えてから登場させる（順次）。 |
| view-transitions#1 | spec-requires-current-behavior | 退場が 300ms で、ガイドラインの退場 200ms より長い。登場も 300ms で、登場 250ms より長い。退場と登場の長さに差がなく、ガイドラインの「退場は短く」に従っていない。ページ遷移が「Begin and end on screen」の 300ms 行に当たるとみるなら一致するが、このページは退場と登場を分けて書いているため、ここでは退場と登場の行を基準にした。 |
| view-transitions#2 | spec-silent | 旧画面の退場と新画面の登場の両方で、ガイドラインの Standard の退場・登場カーブ（accelerate / decelerate）ではなく、単一の ease-out が使われている。 |
| view-transitions#3 | spec-silent | カーブは legacy トークンと一致する（ガイドライン内で legacy と Standard の記述が食い違うため、どちらを正とするかは未確定）。ただし長さは退場 300ms、登場 300ms（遅延 300ms 後）で、pairs の退場 200ms・登場 250ms と一致しない。カードのめくりは 6 つの transition pattern のどれにも当たらないため、パターンとしての適合は判定していない。 |
| navigation-bar#n5 | spec-requires-current-behavior | Old and new route content cross-fade at the same time, and the page header is held across the swap, instead of the exiting screen clearing before the entering screen fades in. |

## T4 出入りする UI に enter / exit の動きを付ける (16)

| ref | spec | finding |
|---|---|---|
| bottom-sheet#1 | spec-silent | The entry fade lasts 160ms, not 250ms, and uses the CSS keyword ease-out instead of the standard decelerate curve. 160ms is not one of the app's duration tokens (m3-sys.css:37-44 gives 150ms and 200ms). The only entry motion in this file is an opacity fade; th |
| bottom-sheet#n0 | spec-requires-current-behavior | On open the sheet is already at its resting position and fades in; it never rises from the bottom edge. The entry slide the guideline prescribes for bottom sheets is missing. (Timing of the fade is already covered by the prior finding on the 160ms ease-out ent |
| fab-and-action-menu#n10 | spec-requires-current-behavior | The FAB stays visible and unchanged through a tab switch. There is no brief disappear and reappear. |
| fab-and-action-menu#n11 | spec-silent | The FAB has no expansion when it first shows. This is conditional on the FAB animating in the spec's sense, so it is low severity. |
| badges-menus#n2 | spec-silent | The shared menu appears and disappears with no enter or exit transition in the audited code. The guideline prescribes a fade and expansion from the trigger, and the menu's own styles provide none. |
| guide-line-and-coach-mark#n0 | spec-silent | ガイドムーメントの一行は、表示も非表示も瞬時に切り替わり、入退場のモーションがない。ガイドラインは tooltips を Enter and exit の対象に挙げている。 |
| guide-line-and-coach-mark#n1 | spec-silent | スポットライト（暗転とハイライト枠）と吹き出しが、フェードもスケールもなく瞬時に出現・消失する。 |
| timetable#n7 | spec-silent | The capsule appears and disappears instantly, with no enter or exit motion, when the list is first scrolled or when the FAB menu opens and closes. |
| discovery-chrome#n1 | spec-silent | The swap tile is part of the animated page snapshot, so it turns together with the body content during a view swap instead of staying put as the control. |
| discovery-chrome#n4 | spec-silent | The results list appears and disappears instantly when search mode starts or ends, where the guideline's search motion fades it. |
| banners-and-feedback#n9 | spec-requires-current-behavior | When a banner is hidden (after install is confirmed, or after signup completes), it disappears instantly. The guideline's enter-and-exit pattern asks for the same slide motion on exit. |
| my-artists#n10 | spec-silent | Entering and leaving edit mode is an instant switch: the Done bar appears at once and the dots become trash buttons at once. |
| my-artists#n11 | spec-matches-m3 | Removal animates, but undo restores the row with no transition, so the rows below it jump down in one frame. |
| settings-route#n10 | spec-matches-m3 | The consent row's description pops in and out with no motion. Only the caret animates. |
| welcome-onboarding-celebration#n9 | spec-silent | The modal scrim appears instantly while its text animates in. The guideline's pattern for a modal calls for a short fade on entry. |
| passkeys-and-entry-routes#n10 | spec-silent | A removed passkey row disappears instantly, with no exit transition, while the rows below jump up. |

## T5 選択・押下のフィードバックの動き（tab・chip・switch・nav） (13)

| ref | spec | finding |
|---|---|---|
| icon-buttons#0 | spec-silent | A toggle icon button (aria-pressed=true) keeps the circular shape when selected instead of changing to a 12px rounded square. |
| text-fields#3 | no-spec-for-this-surface | In this file, hovering the field produces no outline change. The guideline gives a hover outline colour of on-surface. Caveat: only text-field.css was read; a hover rule could exist in another stylesheet. |
| foundations-tokens-states#3 | spec-silent | The app has no disabled state layer (effective opacity 0). The guideline token gives 0.38. The app's disabled look must come from elsewhere, which the read files do not show. |
| navigation-bar#n3 | spec-requires-current-behavior | A tap shows a flat tint that fades in over the tab, not a ripple that spreads through the indicator. |
| navigation-bar#n4 | spec-requires-current-behavior | Hover, press and focus overlays take the tab's content colour (brand-accent when selected, on-surface-variant otherwise), not the on-secondary-container role that the guideline assigns to item state layers. Opacities are correct. |
| icon-buttons#n1 | spec-silent | The shared toggle state (aria-pressed=true) changes only the icon colour. Nothing in the component changes the glyph fill or weight, so the selected state is shown by colour alone. A consumer could still swap the glyph, but the component provides no mechanism  |
| chips#n4 | spec-silent | Chips jump straight to their selected colors and show the check at once. The guideline's motion shows a short color and check transition. The app defines the duration tokens (m3-sys.css:37-39) but does not use them on chips. |
| text-fields#n2 | no-spec-for-this-surface | The focus and error outline colour and border width change instantly. The guideline's motion shows these as short animated transitions. |
| timetable#n3 | spec-requires-current-behavior | A tap on a directly actionable concert card shows a tint change only, with no ripple spreading from the touch point. |
| discovery-chrome#n11 | spec-silent | The bar shows focus but gives no hovered or pressed response. |
| my-artists#n5 | spec-matches-m3 | Hovering or pressing a dot shows no halo and no hover cue besides the pointer cursor. The 40dp state layer is absent. |
| tickets-and-virtual-ticket#n7 | spec-matches-m3 | Taps on the directly actionable row and the ticket face give no touch ripple. The response comes only when the flip or sheet starts. |
| tickets-and-virtual-ticket#n14 | spec-matches-m3 | The Flip button shows no hovered, focused or pressed state. Any focus ring comes only from the browser default, since the shared state-layer rule (shared/styles/state-layer.css:56) does not apply. |

## T6 reduced motion では「消す」のでなく控えめな fade を残す (9)

| ref | spec | finding |
|---|---|---|
| snackbar#n8 | spec-requires-current-behavior | The guideline asks for a subtle fade to remain under reduced motion. The app removes the fade too, so the snack appears and disappears at once. Decorative effects are correctly disabled. |
| timetable#n10 | spec-silent | With reduced motion on, the cards appear with no fade at all, rather than a subtle fade. |
| discovery-chrome#n13 | spec-requires-current-behavior | Under reduced motion the app removes all transitions, including the subtle fade the guideline asks for in place of sliding or scaling. |
| banners-and-feedback#n10 | spec-requires-current-behavior | The guideline keeps a subtle fade under reduced motion and removes only the intense slide and the decorative effects. The app removes the fade together with the slide, so the banner appears with no transition. |
| tickets-and-virtual-ticket#n19 | spec-silent | With reduced motion on, the sides swap in one frame with no fade, where the M3 rule asks for a subtle fade. |
| tickets-and-virtual-ticket#n20 | spec-silent | With reduced motion on, the ticket still leans towards the pointer, a parallax-like effect that the rule says to disable. |
| welcome-onboarding-celebration#n0 | spec-requires-current-behavior | Reduced-motion users get no fade at all. Overlays and content switch in one frame, where the guideline asks for subtle fades. |
| welcome-onboarding-celebration#n1 | spec-silent | The spark flare is decorative and still runs under reduced motion. Its 700 ms duration is a hard-coded literal, not a token, and is 3.5 times the 200 ms the effects spring specifies. |
| accessibility-and-reduced-motion#n2 | spec-silent | A decorative, looping background animation keeps running when reduced motion is on. The guideline asks for decorative effects to be disabled under that setting. |

## T7 キーボード・スクリーンリーダー・拡大文字への対応 (36)

| ref | spec | finding |
|---|---|---|
| dialogs#0 | spec-silent | The basic confirm dialog keeps the native dialog role instead of alertdialog. |
| navigation-bar#11 | spec-silent | No Space handler exists. Native <a> activation on Space is not provided by the browser (inferred from the element type, not read in the files), so Space may not select the tab. |
| icon-buttons#2 | spec-silent | In the files read, the bell has no hover tooltip. A global tooltip mechanism outside these files could still provide one; that was not checked. |
| text-fields#4 | no-spec-for-this-surface | Within this file the caret is on-surface, not primary. Caveat: a global caret-color rule could exist elsewhere; not read. |
| snackbar#n4 | spec-silent | A keyboard user who has moved focus into a snack cannot dismiss it with Esc. They have to wait for the timer or use the close button where one exists. |
| snackbar#n5 | spec-silent | No shortcut to focus an actionable snack exists in this surface, and nothing in it documents one. |
| bottom-sheet#n2 | spec-silent | The handle is a decorative div. Selecting it does nothing, it cannot receive focus, and it has no role or label. The sheet is dismissed by scrim tap, ESC or scroll-swipe, which is compatible with the single-pointer rule, but the handle itself is not an interac |
| bottom-sheet#n6 | spec-requires-current-behavior | The sheet body, which receives focus on open (bottom-sheet.ts:387-389 focusSheet), suppresses its focus ring, and the handle never receives focus, so no focus indicator is drawn for the sheet or its handle. The stated reason for suppression contradicts the tok |
| dialogs#n2 | spec-requires-current-behavior | The only action on the iOS add-to-home-screen step is the dismissive 「あとで」 (Later). The guideline allows a single action only when it acknowledges the message, and a dismissive action is not an acknowledgement. |
| dialogs#n4 | spec-requires-current-behavior | The notification enable failure is shown as a line of text in the same sheet, not in a basic dialog as the guideline names for errors from the confirming action. The message does explain the source and the fix. The one remaining button 「次へ」 (Next) moves on rat |
| fab-and-action-menu#n2 | spec-requires-current-behavior | Focus leaves the close button and lands on the item nearest the FAB (the bottom item). Tab then runs bottom to top. The guideline keeps focus on the close button first and runs top to bottom. |
| fab-and-action-menu#n5 | spec-silent | The icon-only menu button shows no tooltip on hover or focus. |
| fab-and-action-menu#n6 | spec-requires-current-behavior | The closed glyph is an abstract equalizer that does not name the menu's actions. This is a judgement call: the glyph is a filled icon and the open state is clear, but the closed icon does not signal a menu. |
| navigation-bar#n6 | spec-requires-current-behavior | The bar is fixed at 64px, so a larger label cannot add height. At larger text sizes the label has no room inside the bar and spills past it instead of the bar growing. |
| chips#n0 | spec-silent | Enter does not select or deselect a focused filter chip. This contradicts the guideline's Space-or-Enter rule for multi-select chip sets. Note: the prior finding chips#9 credits both Space and Enter to the native checkbox, and that credit is doubtful for Enter |
| chips#n1 | spec-silent | Each chip is a separate Tab stop and the Arrows keys do nothing, so a keyboard user has to Tab through every chip to reach the next control. |
| chips#n5 | spec-silent | A long artist list wraps into more than two rows and then needs scrolling inside a fixed-height box, instead of a horizontal scroll or a reflow method. The guideline says "consider" for scrolling, so this is soft guidance. The severity depends on the artist co |
| tabs#n3 | spec-silent | Arrow keys do not move focus between the date tabs, and Space does not activate a focused tab; only Tab and Enter work. |
| badges-menus#n1 | no-spec-for-this-surface | The stylesheet itself does not block focus, but it explicitly accepts the native `disabled` attribute, which the guideline forbids for menu items (they must stay focusable). Whether any caller uses `disabled` is not visible in these files. Confidence is medium |
| progress-and-loading#n2 | spec-silent | With no label bound, the indicator announces only the generic word 'Loading' and never the process or the content being loaded. The app's own component comment (circular-progress.ts:23) documents the generic default, so the fix is at each call site. |
| progress-and-loading#n3 | spec-matches-m3 | The busy spinner on any button is a decorative pseudo-element with no progressbar role and no label, so assistive technology cannot tell that the action is in progress apart from the still-readable button text. |
| guide-line-and-coach-mark#n2 | spec-silent | キーボードやスイッチ操作の利用者は、コーチマークを閉じる手段を持たない。閉じるのは外側の pointerdown だけ（coach-mark.ts:119-124）。ハイライト対象にフォーカスして Enter を押すと対象の click は走るが、コーチマークは閉じない。 |
| timetable#n4 | spec-silent | Enter does not activate a concert card; only Space does. |
| timetable#n5 | spec-silent | The month-jump buttons show no tooltip on hover; only the screen-reader label exists. |
| discovery-chrome#n0 | spec-silent | Result rows cannot receive keyboard focus and there is no arrow-key navigation, so the keyboard path from the search field to the results does not exist. |
| discovery-chrome#n8 | spec-silent | The bar is about 58px on normal phones, not 56dp, and on small (SE-class) phones it is 40px, shorter than its own 48px input. |
| discovery-chrome#n12 | spec-silent | The swap tile is not prioritized in the focus order; it comes after the genre chips and bubble area. |
| banners-and-feedback#n7 | spec-silent | Both banners appear without a polite live-region announcement. A screen reader user is not told the banner has appeared. The guideline requires this for web snackbars, and the banners are persistent messages of the same kind. |
| my-artists#n0 | spec-silent | Each dot is an unlabeled 8px or 14px circle. Its level name is visible only in the shared column header above the whole table, not next to the choice. |
| my-artists#n6 | spec-silent | Each artist's radio group has no accessible name that identifies the artist or the hype level, so the group's label does not match its category. |
| my-artists#n7 | spec-silent | Arrow keys do not move between artist rows, and Down from the last dot in one row does not reach the next row. Keyboard users must Tab through every row. |
| settings-route#n9 | spec-silent | Keyboard users must Tab through each language button; the arrow keys do nothing, and the radio pattern is not implemented. |
| tickets-and-virtual-ticket#n6 | spec-silent | The ticket row is directly actionable but gives no hover state and is not a tab stop; keyboard users reach the action through a separate button inside it. |
| tickets-and-virtual-ticket#n8 | spec-silent | The ticket face is directly actionable (a tap flips it) but is not a tab stop. The separate Flip button covers keyboard users, so this is a partial gap. |
| inline-error-and-legends#n0 | spec-silent | The flame count encodes tier rank, which is meaningful information, but it is hidden from assistive technology and no accessible label carries it. Only the tier names and scopes reach screen readers. |
| passkeys-and-entry-routes#n5 | spec-silent | After a passkey is removed, focus is lost to the document body instead of going to a sensible control on the page. (Whether cancelling returns focus to the remove button depends on the shared bottom-sheet component, which I did not read.) |

## T8 タップ領域（48dp）の不足 (4)

| ref | spec | finding |
|---|---|---|
| progress-and-loading#2 | spec-matches-m3 | The busy spinner is 16px (1rem), which is below the 24dp minimum for a circular indicator. |
| discovery-chrome#n7 | spec-matches-m3 | The clear X has a 24px box, half the 48dp touch target the guideline gives for trailing icons. |
| tickets-and-virtual-ticket#n15 | spec-silent | The Flip button is 36px, 4px below the M3 default 40dp. |
| accessibility-and-reduced-motion#n6 | spec-silent | Inline text links have a tap area of about one text line, not 48dp. The guideline says 'consider', so this is a soft rule, and inline links in running text are a common exception; the code gives no reason. |

## T9 日本語の行間（言語ごとの line height） (2)

| ref | spec | finding |
|---|---|---|
| foundations-tokens-states#n0 | spec-requires-current-behavior | The app's line heights are the Small (Latin) token values for every style, and the app's primary text is Japanese (Medium language height). Nothing in the read files switches to a medium line height, so Japanese text gets the Small spacing that the guideline s |
| typography-and-icons-usage#n10 | spec-requires-current-behavior | Line heights are fixed at the small (Latin) value for Japanese text, which the guideline puts in the Medium category. |

## T10 先に実測・実機で確認する（コントラスト、スクリーンリーダーの読み上げ） (8)

| ref | spec | finding |
|---|---|---|
| text-fields#2 | no-spec-for-this-surface | The resting outline does not reach 3:1 against the field surface. Hand estimate from the token values (not measured in a browser): surface about #111111 (relative luminance about 0.006), blended outline about #454545 (about 0.060), ratio about 2.0:1. The outli |
| progress-and-loading#0 | spec-silent | The determinate linear track has no stop indicator, and its track contrast with the surface is far below the 3:1 threshold that makes one mandatory. The markup (TSX) was not in scope, so a stop element could exist there. |
| guide-line-and-coach-mark#n3 | spec-silent | コーチマークの文言は、表示されても自動では読み上げられない可能性が高い（実機未確認）。利用者が文言に到達する経路もない。ガイドラインは tooltip の文言を受け取れることを求める。 |
| banners-and-feedback#n3 | spec-requires-current-behavior | The container is 85% transparent with a blur behind it. The text rule says fully opaque. The app's contrast is not measured here, and the guideline's own transparency example suggests that slight transparency is acceptable when text stays legible. |
| tickets-and-virtual-ticket#n16 | spec-silent | The headline is placed on artwork with a soft text shadow and no scrim. Contrast is not measured, so the failure is not confirmed. |
| welcome-onboarding-celebration#n4 | spec-silent | No stop indicator marks the end of the track, and the empty track is nearly invisible against the surface. |
| accessibility-and-reduced-motion#n0 | spec-silent | Clustered outlined chips and outlined buttons are separated from the background by a border of about 1.4:1 contrast, well under the 3:1 the guideline asks for clustered components. The guideline states the 3:1 rule for container colors; these controls have no  |
| accessibility-and-reduced-motion#n1 | spec-silent | The text field's only edge, a 1px border at about 2:1 contrast, is below the 3:1 the guideline asks for non-text elements. The guideline sentence names button containers; a field's border is its container edge, which is my reading. |

## T11 フォームのエラー表示（アイコン・alert・必須マーク） (5)

| ref | spec | finding |
|---|---|---|
| text-fields#n0 | no-spec-for-this-surface | In the error state the field shows only a red border. No error icon is rendered by the audited code, so the error is conveyed by colour alone. |
| purchase-and-form-flows#n0 | spec-silent | Invalid phone numbers are signalled by a red border and red text only; no icon is shown inside the field. |
| purchase-and-form-flows#n1 | spec-silent | The phone field's error text has no alert role, so a screen reader user is not told about the error when it appears. |
| purchase-and-form-flows#n2 | spec-silent | Both required fields have no asterisk, no required attribute, and no explanation that required fields are marked. |
| simple-pages#n0 | spec-silent | The invalid email state is marked only by a red sentence under the field and aria-invalid. No icon marks the field as invalid, which the guideline recommends for users who cannot rely on colour. |

## T12 文言の不整合（英語のままの画面など） (1)

| ref | spec | finding |
|---|---|---|
| simple-pages#n1 | no-spec-for-this-surface | The not-found fallback, the screen a fan reaches from any mistyped URL, shows English-only copy while the rest of the app is localised through the i18n catalog. |

## T13 長い文字列・大きな数値での表示崩れ防止 (5)

| ref | spec | finding |
|---|---|---|
| buttons#6 | spec-silent | The button css does not keep the label on one line, so a narrow or constrained button can wrap or clip its label. The guideline forbids both. |
| chips#2 | spec-silent | Long artist names are never shortened or truncated. The label overflows the chip and the sheet instead of truncating. The 20-character limit is not enforced in code. Conditional on the artist name data, which was not read. |
| cards-and-lists#1 | spec-silent | Every list item is center-aligned regardless of height or line count. Items with three or more lines (label plus supporting text that wraps to 3+ lines, which is possible because the supporting text has no line limit, see the supporting-text finding) keep cent |
| badges-menus#n0 | spec-silent | The unread count is never shortened. From 10000 unread onward the label is five or more characters, which exceeds the four-character limit and the 16x34dp max-count size (md.comp.badge large max character count), and the pill grows past the bell into the heade |
| guide-line-and-coach-mark#n7 | spec-silent | 対象が画面の左右端にあると、ヒントやコーチマークの文字が画面外に切れて見えうる。ガイドラインは 8dp 単位で画面内に収めることを求める。描画では未確認の推定。 |

## K9 switch の寸法と押下の動きを 1 組で決める（44×24 のまま / 52×32 にして handle を拡大） (7)

| ref | spec | finding |
|---|---|---|
| switch#0 | spec-silent | Track is 44x24, not 52x32 (about 15% narrower and 25% shorter). |
| switch#1 | spec-silent | Handle is a fixed 20px in every state. Unselected is 4px larger than spec (16), selected is 4px smaller (24), and the pressed size (28) is not implemented in these files. |
| switch#2 | spec-silent | The app's on state has the same handle size as the off state, so the size cue the page describes is absent. |
| switch#n0 | spec-requires-current-behavior | The handle never changes size on press, drag or click in the listed files. The guideline makes the handle grow in those interactions. |
| settings-route#n1 | spec-silent | The track is 44x24px, not 52x32px, on every switch row and consent row on this surface. |
| settings-route#n3 | spec-silent | The handle is 20px in the off, on and pressed states. The off handle should be 16px, the on handle 24px and the pressed handle 28px. |
| settings-route#n4 | spec-requires-current-behavior | Pressing or toggling a switch does not change the handle size. Only the position and track colour animate. |

## K10 ナビゲーションバーの選択 icon を filled にする（filled 版の icon が要る） (4)

| ref | spec | finding |
|---|---|---|
| navigation-bar#n1 | spec-silent | The selected tab shows the same outline icon as the unselected tabs. The icon never fills or gets heavier. |
| navigation-bar#n2 | spec-silent | No outline-to-filled icon transition on selection. The only animated changes are the colour and the corner radius of the tab. |
| typography-and-icons-usage#n9 | spec-silent | The icon component cannot show an active or selected state through weight, fill or grade. |
| typography-and-icons-usage#n13 | spec-requires-current-behavior | The icon set is hand-drawn SVG, so none of the four variable axes are available. This is the root cause of the stroke, optical size and active-state findings above. |

## K2 snackbar と banner の方針（自動消去・アイコン・action の見た目） (11)

| ref | spec | finding |
|---|---|---|
| snackbar#0 | spec-requires-current-behavior | A snack with an action auto-dismisses after 10 s unless the caller passes its own duration (for example Infinity). |
| snackbar#1 | spec-requires-current-behavior | Every snack shows a severity icon before the message by default. The only opt-out is a per-snack `icon: null` (snack.ts:17-22). |
| snackbar#2 | spec-requires-current-behavior | The container is a brand gradient (info) or a severity colour, not the inverse-surface role. The container is opaque, as the guideline asks. |
| snackbar#5 | spec-silent | Nothing caps the message at two lines, so a long message can wrap to three or more lines and the surface grows past the guideline's two-line size. A caller could still keep messages short; the CSS does not enforce the limit. |
| snackbar#7 | spec-requires-current-behavior | A snack that stays until the person acts (duration Infinity, for example the update snack) leaves without being dismissed when another snack is waiting, then returns. The guideline says it stays until dismissed; the one-at-a-time rule (line 424) is the reason  |
| snackbar#n2 | spec-requires-current-behavior | The label and the action are both pure white, so the action is not distinguished by colour. The guideline's token gives the action label the purple inverse-primary role. |
| snackbar#n3 | spec-requires-current-behavior | The action is a tinted, bordered button, not a plain text button. The fill is translucent, so whether it counts as 'filled' is a judgement. Severity low. |
| snackbar#n6 | spec-requires-current-behavior | Every non-action snack on web auto-dismisses after 4 to 10 s. The surface cannot ensure the inline feedback the guideline requires, and the files do not show that each caller provides it. This is separate from the action-snack timing already reported. |
| banners-and-feedback#n1 | spec-requires-current-behavior | Both banners use a filled button as the single action. The guideline says snackbar actions should be text buttons, and filled buttons draw too much attention for a snackbar. |
| banners-and-feedback#n6 | spec-matches-m3 | The signup banner's message begins with a bell emoji as a leading icon. The guideline says a snackbar should carry no icon. The judgment is that an emoji functions as an icon here; a plain text label would avoid the issue. |
| banners-and-feedback#n8 | spec-requires-current-behavior | The error banner offers three actions (report by email, reload, dismiss). The guideline caps dialogs at two actions, one confirming and one dismissing. |

## K8 部品の分類を先に決める（日付 tab、hype dots、list の形、badge の位置） (27)

| ref | spec | finding |
|---|---|---|
| chips#0 | spec-silent | Unselected artist chips have no leading icon, no interaction label and use outline variant, so none of the listed methods is met. The 12% white border is roughly 1.4:1 against the surface (hand estimate from tokens.css:160 and :164, not measured). The journey  |
| chips#1 | spec-silent | When the user has only one artist with upcoming concerts, the artist facet shows a single chip. The code has no guard for this. Conditional: the countedArtists source was not read, so it may already filter this case. |
| tabs#0 | spec-silent | The active tab is shown by a filled container, not by an underline indicator; there is no 3dp (primary) or 2dp (secondary) active indicator at all. |
| tabs#1 | spec-silent | The active label uses on-primary (white) on a primary fill; the guideline's active label color is the primary role itself, with no fill behind it. |
| tabs#2 | spec-silent | The container uses the surface-container role (a lighter tonal tier, 22% vs 18% lightness) instead of the surface role the guideline names for the tab container. |
| tabs#3 | spec-silent | The container is fully rounded (9999px) where the guideline specifies a corner radius of 0. |
| tabs#4 | spec-silent | The tab container is 56 px tall (48 px tab plus 4 px padding on each side), 8 px more than the 48 dp container height; the label row itself matches 48. |
| tabs#5 | spec-silent | No 1 dp bottom divider in surface-variant is rendered under the tab container. |
| tabs#6 | spec-requires-current-behavior | The app switches the selected state with no animated change, while the guideline shows the color change and the indicator moving to the tapped tab. Timing values are not in the guideline, so only the presence of the motion is compared. |
| badges-menus#0 | spec-silent | The large badge is placed partly outside the 24px icon bounding box and over the icon's corner, not inside the bounding box at the upper trailing edge. This matches the Don't "place the badge over the icon". |
| bottom-sheet#n4 | spec-silent | The modal help sheet can open above 50 percent of the screen when its content is tall. Whether it does for a given page depends on the rendered content height, which the code alone cannot measure. |
| tabs#n0 | spec-requires-current-behavior | Switching between date tabs has no motion in this component; the guideline pairs tabs (peer destinations) with a lateral slide. |
| tabs#n1 | spec-matches-m3 | A tapped date tab shows no ripple or press feedback in this component. |
| tabs#n2 | spec-matches-m3 | The date tabs have no hover or pressed state layer in this component's CSS; the guideline gives 0.08 hover and 0.1 pressed layers over the tab. |
| tabs#n4 | spec-silent | Where the shared focus ring is applied, its offset is 2px outside the element; the guideline places the 3dp ring 3dp inside. Thickness matches. |
| tabs#n5 | spec-silent | Date labels are set in Noto Sans JP (the plain face stack), not Roboto, so the letterforms differ from the guideline's typeface. Size, line height and weight match. |
| progress-and-loading#n5 | spec-requires-current-behavior | Every short wait in this surface uses the indeterminate circular indicator. The loading indicator that M3 Expressive recommends for these waits is not used. This applies only if the app adopts M3 Expressive, since the M3 classic page still lists the circular i |
| discovery-chrome#n2 | spec-silent | Switching between the two peer views uses a card flip, not the grouped horizontal slide the Lateral pattern prescribes. |
| my-artists#n1 | spec-requires-current-behavior | Every artist's single-select radio group is a horizontal row of four choices, which the guideline says to avoid. |
| my-artists#n2 | spec-silent | Unselected dots use the outline-variant role, a 12% alpha white, instead of the on-surface-variant role the guideline names for unselected radios. |
| my-artists#n3 | spec-requires-current-behavior | The selected dot is coloured with each artist's own colour, not the Primary role, so selected-state colour varies by row. |
| my-artists#n4 | spec-requires-current-behavior | The radio's visible icon is 8 to 14px, not 20dp, and has no 40dp state layer. The 48px target is met. |
| settings-route#n0 | spec-requires-current-behavior | The default button is a 12px rounded rectangle, not the Round (full-radius pill) that the guideline makes the default shape. Only the pressed state (8px, button.css:63-65) follows the Expressive square morph; the resting shape is the square variant. |
| settings-route#n2 | spec-silent | The off state has no outline, so the unselected track is a filled chip rather than the outlined track the guideline specifies. |
| settings-route#n7 | spec-silent | Settings rows are baseline-style square list items with hairline dividers, not the segmented round-cornered expressive list. |
| settings-route#n8 | spec-silent | The language options use 12px corners whether selected or not, so there is no shape morph. The guideline gives 16px for selected items and 4px inner and 16px outer for unselected ones. |
| purchase-and-form-flows#n5 | spec-silent | Moving from count to personal details to payment to confirm, and back, is an instant swap with no directional motion. |
