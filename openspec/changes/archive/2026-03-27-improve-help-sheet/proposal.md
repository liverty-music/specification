## Why

The page help sheet has two problems: poor readability due to insufficient contrast between the sheet background and the app surface, and content that doesn't match each page's context well enough to serve as a useful reference. Additionally, help is currently only accessible during onboarding — users who complete onboarding lose access to the `?` button entirely.

## What Changes

- Remove the `isOnboarding` gate on the `<page-help>` component so the `?` icon is always visible in the page header (Discovery, Dashboard, My Artists)
- Auto-open behavior remains onboarding-only (no change to localStorage-based first-visit logic)
- Fix the `<if condition.bind>` rendering bug that displays all page sections simultaneously instead of only the active page's content
- Revise help content per page to serve as a concise reference (not a tutorial):
  - **Discovery**: tap to follow, unfollow from My Artists, genre tabs and search bar
  - **Dashboard**: three-stage model (HOME/NEAR/AWAY) with stage colors, card tap for detail
  - **My Artists**: four Hype levels with notification scope, dot-tap interaction, practical tip ("start with Home")
- Remove content that belongs to other UI surfaces:
  - Follow count display (belongs in persistent UI, not help)
  - Account registration note (handled by signup-prompt-banner)
- Apply existing design tokens to improve readability:
  - Use `--color-surface-overlay` for a lighter sheet background
  - Apply `--color-stage-*` tokens to Dashboard stage labels
  - Replace `opacity: 0.7` text with `--color-text-secondary` for proper contrast
  - Use `--font-display` for help titles

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `onboarding-page-help`: Help icon becomes always-accessible (not gated by onboarding state). Content requirements updated per page. Visual design requirements added.

## Impact

- **Frontend only** — `page-help` component (TS, HTML, CSS), `bottom-sheet` CSS, i18n files (en/ja)
- **Route templates** — `discovery-route.html`, `dashboard-route.html`, `my-artists-route.html` (remove `if.bind="isOnboarding"` from `<page-help>`)
- **No backend or protobuf changes**
