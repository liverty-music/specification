## Why

The current onboarding flow suffers from poor UX: coach marks are too small and easily missed, the dashboard layout doesn't resemble a festival timetable, hype indicators clutter artist names with emoji badges, and key transition moments (like dashboard generation) lack emotional payoff. Users can scroll past coach marks, miss the CTA to generate their dashboard, and get stuck after tapping a concert card with no guidance to the next step.

## What Changes

- **Coach mark overhaul**: Darker overlay (75%), larger tooltips with brand accent color, spotlight pulse ring animation, scroll lock during active coach marks
- **Dashboard header redesign**: Replace "Live Highway / Home Area / Region / Others" with festival-style sticky lane headers: HOME STAGE / NEAR STAGE / AWAY STAGE
- **Dashboard lane layout**: Change column ratio from 50:30:20 to equal 33:33:33
- **Artist name typography**: Dynamic font sizing via CSS container queries with minimum readable size; allow line breaks, adjust card height accordingly
- **Hype visualization**: Replace emoji badges (🔥) with border gradient + glow intensity (A) combined with neon text-shadow effect (C), scaled by hype level
- **Event detail sheet**: Convert from `<dialog>.showModal()` to `popover="manual"` to resolve top-layer stacking conflicts with coach marks
- **Onboarding Step 1 CTA**: Replace "Generate Dashboard" button with spotlight on nav-bar Dashboard icon; require concert data for all 3 followed artists before showing CTA; progress bar shows concert search completion
- **Celebration overlay**: Add "タイムテーブルが完成しました！" overlay with confetti/particle effect (2-3s) between discovery and dashboard
- **Dashboard lane introduction**: Sequential spotlight of each STAGE header with explanatory coach marks before spotlighting first card
- **Step 4 guidance**: After detail sheet, spotlight My Artists nav tab with "アーティスト一覧も見てみよう！" message
- **Nav bar visibility**: Show on all pages except Welcome; rely on existing route guards for navigation restriction during onboarding
- **Remove loading sequence from onboarding**: Loading screen (Step 2) already skipped; clean up any remaining references
- **Coach mark messages**: "タイムテーブルを見てみよう！" (Step 1 CTA), lane explanations (Step 3), "アーティスト一覧も見てみよう！" (Step 4)

## Capabilities

### New Capabilities
- `onboarding-celebration`: Celebration overlay with particle effects shown after dashboard generation, before dashboard reveal
- `dashboard-lane-introduction`: Sequential spotlight walkthrough of STAGE headers during onboarding Step 3

### Modified Capabilities
- `onboarding-tutorial`: Add lane introduction sub-steps to Step 3; change Step 1 CTA from button to nav-bar spotlight; add concert data readiness gate; update Step 4 guidance message; update coach mark visual design (overlay darkness, tooltip size, pulse ring)
- `onboarding-guidance`: Progress bar tracks concert search completion for followed artists; update CTA trigger condition from followedCount >= 3 to concert data ready for 3+ artists
- `typography-focused-dashboard`: Change lane ratio to 33:33:33; rename headers to HOME/NEAR/AWAY STAGE; add sticky festival-style header; dynamic font sizing via container queries
- `passion-level`: Replace emoji badge hype indicators with border gradient + glow + neon text-shadow system
- `concert-detail`: Convert event-detail-sheet from showModal() to popover="manual"
- `app-shell-layout`: Show nav bar on all pages except Welcome (currently hidden during discover/loading too)

## Impact

- **Frontend components**: coach-mark, live-highway, event-card, event-detail-sheet, bottom-nav-bar, discover-page, dashboard
- **Frontend services**: onboarding-service (step logic), dashboard-service (lane config)
- **CSS**: New keyframe animations (spotlight pulse, hype glow, celebration particles), container query font sizing
- **i18n**: New/updated translation keys for coach mark messages and celebration text
- **No backend changes**: All changes are frontend-only
- **No proto changes**: Lane naming is UI-only; proto fields (home/nearby/away) unchanged
