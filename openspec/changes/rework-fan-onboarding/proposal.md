## Why

A guest who follows artists and then chooses a home area on the Dashboard never sees the timetable-ready celebration and never leaves onboarding, which we reproduced on production on 2026-10-24. The discovery coach mark disappears on the next tap and never comes back, the post-signup celebration reads over the empty-state text, the post-signup sheet asks for two things with equal weight, and the analytics notice that the onboarding story requires is reachable from nowhere. The living specs for discovery, the coach mark and onboarding have also drifted far from the code (37 mismatches: requirements for removed features, renamed screens, a polling flow that no longer exists), so they no longer tell anyone what the first run does.

## What Changes

- **Dashboard first arrival**: the timetable-ready decision runs on every arrival path, including the one where the guest picks a home area first. The light celebration shows only when the guest follows at least one artist and the timetable holds at least one concert, and its copy states the real numbers ("5組のアーティストの12公演が見つかりました"). With follows but no concert, the empty state guides instead.
- **Discovery progress row**: a row under the genre chips shows how far the timetable is from ready. Every follow moves it: a follow without a found concert adds 1/5, one with a found concert adds 1/3. When it reaches ready it turns into a button to the Dashboard. **The discovery coach mark is removed** (the coach mark stays for the Welcome demo).
- **Post-signup celebration**: a darker, blurred scrim, a centre burst of varied confetti, a bouncing headline, a sound that follows the mute setting and a vibration where supported. Copy: 「ようこそ！もうライブは見逃さない」 / 「新着ライブは、Liverty Music が追いかけます！」.
- **Post-signup sheet becomes two steps, one primary action each**: step 1 says the search for the fan's followed artists has started and asks to turn on notifications; step 2 asks to add the app to the home screen, shown only where the browser can install it and it is not installed. On iOS without the app installed, the sheet shows the add-to-home-screen steps instead, because web push there works only for an installed app.
- **Where push permission is asked**: the post-signup sheet, a snack offer when a signed-in fan changes an artist's hype on My Artists, and the Settings toggle. The hype offer appears at most once per session and stops after the fan declines it 3 times; it never appears after the browser blocked notifications. **The second-session notification toast is removed.**
- **Welcome analytics line**: under both Get Started buttons, 「使いやすさの改善のため、利用状況を分析しています。分析に名前やメールアドレスは使いません。」 with links to turn analytics off and to the details page. This replaces the onboarding "final step" notice that nothing ever showed.
- **Spec drift**: delete requirements for removed features (popover guide, guidance overlay, orb "View Live Schedule" button, search-status polling, `onboardingStep` migration, `redirectBasedOnStatus`, coach-mark SVG arrow and View Transitions) and rewrite the rest to match the code (route names, the Home tab, follow-store behaviour, snack copy and timing, coach-mark top-layer model).
- **Copy fixes**: My Artists help describes the dot selector and the Edit action in the action menu; Settings stops calling signed-in analytics "anonymous".
- **Code fixes found on the way**: a failed follow from search results shows an error snack.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `stories/complete-onboarding`: remove the search-status polling, `redirectBasedOnStatus` and legacy-migration requirements; the latch fires on every successful sign-in or sign-up; the analytics notice moves from a final onboarding step to the Welcome line.
- `components/infrastructure/fan/web/route/discovery`: progress row replaces the coach-mark trigger; delete and rewrite the drifted requirements.
- `components/infrastructure/fan/web/route/dashboard`: the data-ready side effects also fire after the home area is chosen on arrival.
- `components/infrastructure/fan/web/route/welcome`: the analytics line under the Get Started buttons.
- `components/infrastructure/fan/web/route/my-artists`: the push offer on hype change; help content matches the current controls.
- `components/infrastructure/fan/web/global/celebration-overlay`: light-tier conditions and copy with counts; post-signup copy, scrim, burst, sound and vibration.
- `components/infrastructure/fan/web/global/post-signup-dialog`: two-step sheet and the iOS branch.
- `components/infrastructure/fan/web/global/notification-prompt`: becomes the in-app push offer (where it appears, the per-session and 3-decline limits); the second-session toast goes.
- `components/infrastructure/fan/web/global/coach-mark`: no discovery use; requirements rewritten to the fixed-overlay model the code uses; SVG arrow and View Transition requirements removed.
- `components/infrastructure/fan/web/global/page-help`: help is opened from the action menu, not a `?` icon; My Artists help names the current controls.
- `components/infrastructure/fan/web/global/app-shell`: the shell no longer hosts the notification prompt or a coach mark.
- `components/infrastructure/fan/web/global/bottom-nav-bar`: the Home tab attribute no longer serves a coach mark.

No entity, operation or usecase changes: every behaviour here is in the fan web app. The stories `stories/get-notified-of-new-concerts` and `stories/set-hype-for-an-artist` are unchanged; this change only moves where the browser permission is asked.

## Impact

- **frontend only.** Discovery route and a new progress component, Dashboard route (load path and celebration decision), celebration overlay, post-signup dialog, My Artists route (hype change), Welcome route, app shell (notification prompt removed), notification manager (no API on iOS Safari), translations (ja, en), page help.
- No proto, backend or cloud-provisioning change. No new persistent setting.
- New localStorage key for the push-offer decline count; existing keys `ui.notificationPromptDismissed` and `ui.onboardingCompletedSessionCount` lose their reader (see design for cleanup).
- Out of scope, filed separately: past concerts (July 2026) shown on the timetable on 2026-10-24; sending a returning guest from `/` to the timetable; a dismiss control on the PWA banner and a rework of the prompt coordinator; unused translation keys; Welcome "Log In" clearing guest follows; telling the app when a server-side concert search completes.
