## 1. Fix Rendering and Accessibility

- [x] 1.1 Replace three `<if condition.bind>` blocks in `page-help.html` with `switch`/`case` on the `page` bindable to ensure mutual exclusivity
- [x] 1.2 Remove `if.bind="isOnboarding"` from `<page-help>` in `discovery-route.html`, `dashboard-route.html`, and `my-artists-route.html`
- [x] 1.3 Remove `followedCount` bindable from `page-help.ts` and the `followed-count.bind` attribute from `discovery-route.html`

## 2. Update Help Content

- [x] 2.1 Update Discovery help content in `page-help.html`: tap to follow, unfollow from My Artists, genre tabs and search bar
- [x] 2.2 Update Dashboard help content in `page-help.html`: three stages with stage-colored labels, card tap for detail
- [x] 2.3 Update My Artists help content in `page-help.html`: four Hype levels with notification scope, dot-tap interaction, practical tip for Home level
- [x] 2.4 Update Japanese i18n strings in `locales/ja/translation.json` under `pageHelp.*` — remove `followedCount`, `accountNote`; add new keys for updated content
- [x] 2.5 Update English i18n strings in `locales/en/translation.json` under `pageHelp.*` — same changes as Japanese

## 3. Improve Visual Readability

- [x] 3.1 Override sheet background in `page-help.css`: set `background: var(--color-surface-overlay)` on `.page-help-content`
- [x] 3.2 Apply `font-family: var(--font-display)` to `.page-help-title`
- [x] 3.3 Replace `opacity: 0.7` on `.page-help-note` and `.page-help-count` with `color: var(--color-text-secondary)`
- [x] 3.4 Add stage-colored label styling for Dashboard help using `--color-stage-home`, `--color-stage-near`, `--color-stage-away`

## 4. Update Tests

- [x] 4.1 Update `page-help.spec.ts`: remove `followedCount` tests, add test for always-visible `?` icon (not gated by onboarding), verify `switch`/`case` renders only active page content
