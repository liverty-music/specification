## Context

The `page-help` component provides contextual help via a bottom-sheet triggered by a `?` icon in the page header. Currently it is gated by `if.bind="isOnboarding"` in each route template, making it invisible after onboarding completes. The help content suffers from two issues: a rendering bug where all three page sections display simultaneously (the `<if condition.bind>` conditional is not filtering correctly), and poor visual contrast between the sheet surface and the app background.

Key files:
- `src/components/page-help/page-help.{ts,html,css}` — component logic, template, styles
- `src/components/bottom-sheet/bottom-sheet.css` — sheet surface styling
- `src/routes/{discovery,dashboard,my-artists}/*-route.html` — route integration
- `src/locales/{en,ja}/translation.json` — i18n content under `pageHelp.*`
- `src/styles/tokens.css` — design tokens

## Goals / Non-Goals

**Goals:**
- Make the help `?` icon always accessible on Discovery, Dashboard, and My Artists pages
- Fix the conditional rendering so only the active page's help content is shown
- Revise help text per page to serve as a concise reference for both onboarding and returning users
- Improve sheet readability using existing design tokens

**Non-Goals:**
- Adding help to pages beyond Discovery, Dashboard, My Artists
- Illustrated or animated help content
- Changing the bottom-sheet primitive itself (scroll-snap, popover API, dismiss behavior)
- Adding follow-count display or progress indicators to help (these belong in persistent page UI)

## Decisions

### 1. Remove `isOnboarding` gate from route templates, keep auto-open logic in TS

Remove `if.bind="isOnboarding"` from `<page-help>` in the three route templates. The component always renders, but auto-open still only fires during onboarding (the `attached()` check in `page-help.ts` already gates on `this.onboarding.isOnboarding`).

**Why**: Simplest change — one attribute removal per route. No new state management needed.

### 2. Fix conditional rendering with `switch`/`case` pattern

Replace the three separate `<if condition.bind="page === '...'">` blocks with Aurelia's `switch`/`case` template controller on the `page` bindable. This ensures mutual exclusivity and avoids the current bug where multiple `<if>` blocks may all evaluate.

**Alternative considered**: Debug why `<if condition.bind>` renders all sections. Rejected because `switch`/`case` is semantically correct for mutually exclusive content and prevents recurrence.

### 3. Apply existing tokens for visual improvement

| Element | Current | Change |
|---------|---------|--------|
| Sheet background | `--color-surface-raised` (oklch 22%) | `--color-surface-overlay` (oklch 26%) |
| Help title font | `--font-body` (inherited) | `--font-display` (Righteous) |
| Muted text | `opacity: 0.7` | `color: var(--color-text-secondary)` (oklch 82%) |
| Dashboard stage labels | plain white text | `color: var(--color-stage-home/near/away)` per label |

All tokens already exist in `tokens.css`. No new tokens needed.

**Where to apply**: Sheet background is controlled via a `--sheet-bg` CSS custom property added to `bottom-sheet.css` (with a fallback of `--color-surface-raised`). `page-help.css` sets `--sheet-bg: var(--color-surface-overlay)` scoped to `bottom-sheet` within the `page-help` component. This approach ensures the handle bar and content area share the same background, preventing a visual step between them. Stage colors apply only to the Dashboard help section via `data-stage` attribute selectors.

**Why not override on `.page-help-content` directly**: Setting `background` only on the slotted content element (`.page-help-content`) would leave the `.handle-bar` inside `bottom-sheet`'s `.sheet-body` rendering in the old `--color-surface-raised` color, creating a visible band above the content area.

### 4. Content structure per page

**Discovery:**
- Tap bubbles to follow
- Unfollow from My Artists page
- Genre tabs and search bar available

**Dashboard:**
- Three stages (HOME/NEAR/AWAY) with stage-colored labels
- Card tap opens concert detail

**My Artists:**
- Four Hype levels with notification scope
- Dot tap to change level
- Practical tip: "Start with Home for artists you're curious about"

Content that is explicitly excluded:
- Follow count (not help's responsibility)
- Account registration note (handled by `signup-prompt-banner`)
- Swipe gestures (not applicable to current UI)

## Risks / Trade-offs

- [Always-visible `?` button may confuse non-onboarding users who don't need help] → Acceptable: the button is small and non-intrusive. Users who don't need it will ignore it. Users who do need it will find it.
- [Sheet background change affects all bottom-sheet usages if applied globally] → Mitigated: `--sheet-bg` custom property defaults to `--color-surface-raised`, so all other bottom-sheet usages are unaffected. Only `page-help` overrides it.
- [`switch`/`case` requires Aurelia 2 template controller support] → Already available in Aurelia 2. Verify syntax in implementation.
