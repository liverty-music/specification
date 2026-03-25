## Why

The current onboarding flow over-constrains users with sequential forced gates, revert logic, and silent click-blocking, creating a perception that the app is broken before users have experienced its core value. The dashboard — the product's key differentiator — receives fewer than 12 seconds of guided attention before users are pushed away from it. This redesign removes the linear rails, shifts guidance to a pull-based model, and ensures the timetable experience lands first.

## What Changes

- **DETAIL onboarding step removed** — the step sequence becomes LP → DISCOVERY → DASHBOARD → MY_ARTISTS → COMPLETED
- **Discovery progression condition relaxed** — from "3 artists with concerts" to "5 follows OR 3 with concerts" (whichever comes first); coach mark shows for 2 seconds then fades (user navigates at their own pace)
- **Lane Intro becomes tap-to-advance** — auto-timer removed; Home Selector appears inline during the HOME phase with "居住エリア" framing; Lane Intro copy is dynamically interpolated with selected prefecture
- **Celebration Overlay repositioned** — moves to after Lane Intro, serving as the explicit end of guided onboarding; tap-to-dismiss (no timer); adds "自由にタイムテーブルを触ってみよう" message; DASHBOARD step completes on Celebration open
- **Concert card tap opens Detail Sheet** — card taps now open the EventDetailSheet; opening the sheet triggers end-of-guidance (no more spotlight-to-My-Artists sequence)
- **`router.load()` removed from coach mark click handler** — navigation delegates to nav href; blocker divs and scroll lock remain active during Lane Intro
- **Non-spotlighted nav tabs visually disabled** during onboarding (opacity 0.3 + aria-disabled)
- **Hype revert removed** — guest hype changes are persisted to localStorage (merged to backend on signup); HypeNotificationDialog removed; hype explanation moves to PageHelp
- **PageHelp component introduced** — persistent `?` icon in Discovery, Dashboard, and My Artists; auto-opens on first visit per page (onboarding context); bottom-sheet per-page guide content
- **Discovery popover snack replaced** — 5-second guide snack removed; `hasUpcomingEvents` snack retained
- **PostSignupDialog introduced** — appears on auth-callback → /dashboard redirect after signup; covers notification permission + PWA install in one dialog
- **Guest data banner copy updated** — reframed around saving follows and enabling notifications
- **Welcome page gains dashboard preview** — real dashboard component embedded with fallback artist list for live data; "アカウント不要でお試しいただけます" copy added
- **Empty dashboard state** — API error and zero-concert states get dedicated UI; no auto-redirect to My Artists

## Capabilities

### New Capabilities

- `onboarding-page-help`: Persistent `?` icon and per-page bottom-sheet guide for Discovery, Dashboard, and My Artists pages. Auto-opens on first onboarding visit. Replaces popover snack and HypeNotificationDialog.
- `post-signup-dialog`: Dialog shown after auth-callback redirects to dashboard on first signup. Covers push notification opt-in and PWA install prompt in a single, non-competing surface.
- `welcome-dashboard-preview`: Embedded live dashboard component on the Welcome page using a curated popular-artist fallback list. Demonstrates the product before sign-up.

### Modified Capabilities

- `frontend-onboarding-flow`: Step sequence change (DETAIL removed), progression condition relaxed (5 follows OR 3 with concerts), DASHBOARD completion trigger moved to Celebration open
- `onboarding-tutorial`: Lane Intro becomes tap-to-advance; Celebration repositioned after Lane Intro; Home Selector inline in HOME phase; card tap opens real Detail Sheet; My Artists spotlight sequence removed; nav tabs visually disabled during guided phase
- `dashboard-lane-introduction`: Home Selector timing and framing changed (inline in HOME phase, "居住エリア" copy); Lane Intro copy dynamically interpolated; auto-advance timer removed
- `onboarding-celebration`: Position changed (after Lane Intro); content updated; timer → tap-to-dismiss; triggers DASHBOARD step completion on open
- `onboarding-spotlight`: `router.load()` removed from click handler; scroll lock and blocker divs unchanged
- `my-artists`: Hype revert logic removed; guest hype persisted to localStorage; HypeNotificationDialog removed; hype explanation delegated to PageHelp
- `guest-data-merge`: Hype level added to guest data merge payload on signup
- `signup-prompt-banner`: Copy updated to emphasize follow data persistence and notification benefit
- `landing-page`: Dashboard preview component embedded; guest-friendly copy added

## Impact

- **Frontend only** — no proto or backend changes required
- Affected routes: `welcome-route`, `discovery-route`, `dashboard-route`, `my-artists-route`, `auth-callback-route`
- Affected services: `onboarding-service`, `guest-service`, `follow-service-client`
- Affected components: `coach-mark`, `celebration-overlay`, `user-home-selector`, `hype-notification-dialog` (removed), `notification-prompt`
- New components: `PageHelp`, `PostSignupDialog`
- i18n: Lane Intro keys updated; new PageHelp guide strings; banner copy changed
- `onboarding.ts` entity: DETAIL step removed from enum and step map
