## Context

See proposal.md for the motivation. Everything here is in the fan web app (frontend repository); no RPC, proto or backend behaviour changes. The facts the design rests on, checked on 2026-10-24:

- The Dashboard loads twice for a guest without a home area: once while the home-area sheet is open, once after the choice. The second load takes the cached fast path in `DashboardRoute.loadData()`, which never sets `timetableLoaded` back to `false`, so `timetableLoadedChanged()` does not fire and neither `maybeCelebrate()` nor `maybeFinishOnboarding()` runs. Reproduced on production with a fresh guest: no celebration, and `onboardingComplete` never written.
- Discovery learns that an artist has concerts only from `ConcertService.ListByArtist` right after a follow, and only for concerts already in the catalog. A search for a never-searched artist runs on the server later (stories/follow-an-artist) and the app is not told when it ends. Guest follows reach the server only at sign-up (stories/merge-guest-data-on-signup), which is when their first searches start.
- iOS Safari exposes no `Notification` API outside an installed home-screen app (WebKit, "Web Push for Web Apps on iOS and iPadOS"). Today `NotificationManager.requestPermission()` returns `'denied'` there and the post-signup button does nothing visible.
- Analytics identifies a signed-in fan with the internal user id only (`user-hydration-task.ts`); no name or email is sent. The privacy policy already lists the 外部送信規律 (external-transmission rule) items (data, recipient, purpose) and the country and APPI basis.

## Goals / Non-Goals

**Goals:**
- Every guest who follows and chooses a home area finishes onboarding and sees the celebration when there is something to celebrate.
- Each first-run surface has one job and one primary action; push permission is asked only right after a press, where the fan has shown intent.
- Specs for discovery, coach mark, onboarding and the first-run surfaces describe the code as it is after this change.

**Non-Goals:**
- Telling the app when a server-side concert search finishes (a real "concert found" moment). Filed as a follow-up.
- The PWA install banner, the prompt coordinator, the `/` redirect for returning guests, past concerts on the timetable, and unused translation keys (proposal Impact lists them).

## Decisions

### 1. Make every Dashboard load produce a `timetableLoaded` false→true edge

In the fast path of `loadData()`, set `timetableLoaded = false` before `reflectCachedGroups()` sets it to `true`. `@observable` calls `timetableLoadedChanged(true)` on the second assignment, so the region-select arrival reaches `onTimetableReady()` like the cold path.

Alternative: call `onTimetableReady()` directly from `onHomeSelected()`. Rejected: it adds a second trigger next to the observed one, and the spec requires the decisions to follow observed data arrival (route/dashboard "Data-ready side effects gate on observed data arrival"). `maybeCelebrate()` and `maybeFinishOnboarding()` already guard against running twice (`celebrationShown`, `isOnboarding`).

### 2. Celebration numbers come from the loaded timetable

- Artists: `followStore.followedCount` (guest: the local follow list; signed in: `FollowService.List` response).
- Concerts: the number of distinct concerts in the Dashboard's loaded date groups (guest: `ConcertService.ListByArtists` response `concerts`; signed in: the same RPC the Dashboard already calls). Counted once in `maybeCelebrate()`.

The light tier returns early when either number is 0. The guest empty state already covers 0 follows; the generic empty state 「新しいライブが見つかり次第、ここに並びます」 covers follows without concerts. The latch (`maybeFinishOnboarding`) keeps its own condition (≥1 follow), so a guest whose artists have no concerts still finishes onboarding.

### 3. Discovery progress row is a DOM row in the layout grid, not part of the canvas

A new `<onboarding-progress>` component sits in the discovery grid between the genre row and the bubble area. It is hidden in search mode with the genre row, and hidden when `isOnboarding` is false. The bubble area loses one row (about 36 px). The canvas already sizes itself from its container on init and resize, and onboarding never ends while Discovery is shown (the latch runs on the Dashboard and the auth callback), so the canvas never resizes under the fan.

Readiness is a pure function next to the thresholds:

```ts
// constants/onboarding.ts
export function timetableReadiness(followed: number, withConcerts: number): number {
	const without = Math.max(0, followed - withConcerts)
	return Math.min(1, without / DASHBOARD_FOLLOW_TARGET + withConcerts / DASHBOARD_CONCERT_TARGET)
}
```

Inputs: `followStore.followedCount` and `concertStore.artistsWithConcertsCount`, which `ConcertService.ListByArtist` responses fill. Both are observable, so the row updates when a lookup lands after the follow. A guest's lookups re-run on Discovery entry for every stored follow, so the value is right on re-entry too.

Alternatives (the plan asked the user, who chose the row): a ring around the orb (canvas drawing and a separate live region for screen readers) and a pill in the shell page header (a new slot in `page-header`). The previous min-of-two "remaining" count was rejected because a follow without concerts could leave it unchanged.

### 4. Discovery drops the coach mark; the shell coach mark goes with it

`onShowDashboardCoachMarkChanged`, `onCoachMarkTap` and the `ICoachMarkService` use leave `DiscoveryRoute`. Discovery was the only caller of `CoachMarkService`. The Welcome demo renders its own `<coach-mark>` driven by local state. So the shell-level `<coach-mark>` in `app-shell.html` and `CoachMarkService` are deleted, and the `<coach-mark>` component stays for Welcome (coach-mark delta "One non-blocking coach mark rendered by the screen that uses it").

### 5. Celebration effects

- Scrim: `--_scrim` about 74% dark plus `backdrop-filter: blur(6px)`, which replaces the light-scrim-plus-text-lens approach.
- Confetti: about 40 pieces generated in the view model with random CSS custom properties (angle, distance, size, shape, duration, spin). One `@keyframes` reads them, so the burst starts from the centre without 30 hand-written `nth-child` rules.
- Headline: one keyframe that goes 0.8 → 1.1 → 1.0.
- Sound: a new synthesized `playCelebration()` on the existing `AudioEngine`, the Web Audio engine that plays the Discovery pop. It reads the same `muted` and volume settings, so it needs no new setting.
- Vibration: `navigator.vibrate?.([30, 40, 60])`. There is no vibrate on iOS, so it is a no-op there.
- `prefers-reduced-motion`: no confetti, scaling or vibration. The sound still plays unless muted.

### 6. Post-signup dialog becomes a small step machine

Steps: `notify` → `install` → closed, or `iosGuide` → closed. They are chosen when the dialog opens:

- `iosGuide` when `pwaInstall.isIos && !pwaInstall.installed`.
- Otherwise `notify` when `'Notification' in globalThis && Notification.permission === 'default'`, and skipped if not.
- `install` when the browser supports install (`browserSupportsPwa` or a deferred prompt) and the app is not installed. When nothing is left, the dialog does not open.

The count in the step 1 body reads `followStore.followedCount` after the guest merge. The merge runs from `GuestMigrationRequested` in the auth callback, before the redirect, and the dialog opens only after the celebration is dismissed. If the merge has not finished, the count can be low; see Risks.

### 7. One push-offer service replaces the notification prompt

A new `PushOfferService` (frontend service) owns the rules the notification-prompt delta states:

- `shouldOffer()`: signed in, `Notification` API present, permission `'default'`, not offered in this app launch (in-memory flag), and the decline count below 3 (`localStorage['push.offerDeclines']`).
- `offer(snack)`: attaches the 「オンにする」 action to a snack.
- `accept()`: calls `PushServiceClient.create()` inside the press handler, so the browser prompt follows a user gesture, then publishes the outcome snack.
- A snack that times out, or is dismissed without its action, increments the decline count, and so does a browser prompt closed without an answer. The post-signup sheet's ask does not count. This needs a dismissal callback on the snack bar if it does not have one (task).

Callers: the post-signup dialog step 1, which uses `accept()` directly and is not counted against the limit, and My Artists `onHypeChanged` for signed-in fans after the hype RPC succeeds. The "session" in the spec is one app launch, so `ui.sessionCount` and `ui.onboardingCompletedSessionCount` lose their only reader.

Deleted:
- the `notification-prompt` component and its `<notification-prompt>` in the app shell
- `persistOnboardingCompletedSessionCount` and its watch in `pwa-install-service`
- `trackSessionForPrompts`
- the `notification` branch of `PromptCoordinator` (the coordinator stays for `isPostSignupSurfaceOpen`)

Old keys are left in storage; nothing reads them.

Alternatives:
- Keep the toast and add the hype snack. Rejected: three places would ask the same question.
- Offer in Discovery when the catalog already has concerts. Rejected: it reaches only signed-in fans following already-searched artists (see Context).

### 8. Welcome analytics line and the details page

Both Get Started placements in `welcome-route.html` get two lines. 「オフにできます」 links to the Settings analytics toggle and 「詳しく」 links to `/consent`. The `/consent` page stays as the details page that names the recipient, the data and the purpose, and links the privacy policy. Its `analytics.noticeSeen` write is removed, because nothing reads it and the notice is now always visible.

Legal basis:
- 外部送信規律 requires the data, the recipient and the purpose to be notified or published. The privacy policy publishes all three, and the line links to them.
- APPI cross-border transfer relies on the EU adequacy decision, which is stated in the privacy policy.

The line names no country and no vendor, by the user's choice. This is an engineering reading, not legal advice.

### 9. Small code fixes

- A failed follow from search results, or from a bubble tap by a signed-in fan, publishes the existing unused `discovery.followFailed` snack.
- `settings.analytics.toggleDescription` (ja and en) drops "匿名" and says that no name or email is sent.
- The My Artists help text describes the dot selector and Edit in the action menu.

## Risks / Trade-offs

- [The concert count can include concerts the timetable should not show (the open past-concerts issue)] → The count reads the same groups the fan sees, so it is at least consistent with the screen. The past-concerts issue is filed separately.
- [Step 1 shows a low follow count if the guest merge is still running] → The body uses the count only as a fact the fan can check; if it is 0 the generic body is used. Merge normally ends before the redirect.
- [The progress row takes 36 px from the bubble field on narrow screens] → Below 390 px the field already shows at most 30 bubbles, and the row only exists during onboarding.
- [Decline counting depends on the snack timing out] → A fan who switches tabs while the snack is open may be counted once without seeing it; the cap of 3 keeps the effect small.
- [Removing the toast removes the only ask for fans who signed up before this change and never changed hype] → They still have the Settings toggle and the hype offer. There are no real users yet (owner and one tester).

## Migration Plan

- Ship as one frontend PR. There is no data migration; old localStorage keys are ignored.
- Verify on production: unit tests, then the Playwright guest journey used in the investigation (fresh context, analytics blocked). It covers follow → progress row → home area → celebration → `onboardingComplete === 'true'`. The dev environment is stopped, so production is the check.
- Rollback: revert the PR. Nothing persists that the old code cannot read.
