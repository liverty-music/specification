## Context

See proposal.md for why. The fan web is Aurelia 2 with CUBE CSS (no `z-index`, `stylelint.config.js`), the Popover API and CSS Anchor Positioning. Sheets and dialogs live in the top layer. The artist bubbles are drawn on a canvas (`artist-bubbles`, Canvas 2D and Matter.js) with no DOM element per bubble. Help opens on its own on a first visit to Discovery and My Artists during onboarding (`page-help` `auto-open`), and its seen flags are cleared on every sign-up and sign-in (`clearOnboardingSeenFlags()`, called from `userStore.clearGuest()` in the auth callback).

The flows were checked against frontend `main` (0703699e, then 1024b07c) and in a Playwright run with the backend mocked (`e2e/functional/ticket-notify-sign-up.spec.ts`'s mocks, 412×915 Chromium): after a sign-up started from 🔔 the concert sheet opens in front, the confetti celebration runs hidden behind it, shows when the sheet closes, and its dismissal opens the post-signup notification step about new concerts.

The onboarding story map, the information architecture per step and the persona walk-throughs behind these decisions are recorded in `docs/fan-story-map.md` (task 1.1).

## Goals / Non-Goals

**Goals:**
- One mechanism for every guide moment, so the rules of `guide-moment` (one at a time, blocked by sheets, seen per device, replay, analytics) are written once.
- Each moment's condition reads data the screen already loads.

**Non-Goals:**
- No guide for the highlighted cards or the laser effect; fans find them by use.
- No new sound.
- The Welcome demo's coach mark is unchanged.
- No change to the onboarding latch, the hype snack rules or the push offer.

## Decisions

### 1. `IGuideService` owns order, seen marks and reporting

A singleton `IGuideService` (`src/services/guide-service.ts`) holds the moment ids `discovery.follow`, `discovery.swap`, `concerts.filter`, `sheet.notify`, `myArtists.hype` and exposes:

- `request(id)`: a screen calls it when its own condition holds. The service shows the moment unless it is seen, another moment is current, or a blocker is up; when blocked it remembers the request and shows it once when the blocker clears, if the requesting screen is still attached.
- `acted(id)`: the fan used the target; ends the moment and marks it seen.
- `dismiss(id, reason)`: a tap elsewhere or leaving the screen; marks it seen only after 3 s on screen.
- `replay(id)`: from a help 「チュートリアル」 button; ignores the seen mark.
- `current`: observable; the target binds to it.

Blockers are read from the services that already track them: `IBottomSheetTracker.anyOpen` (every bottom sheet, the help sheet and the home-area sheet), `IPromptCoordinator` (post-signup surface) and the Timetable's celebration state, published to the coordinator. `sheet.notify` ignores an open concert sheet, since it lives inside it.

Seen marks are `guide.seen:<id>` in localStorage through a new `src/adapter/storage/guide-storage.ts`; `clearOnboardingSeenFlags()` does not touch them. Alternatives: account-side seen marks (needs proto and backend for a hint) — rejected; each screen's condition already keeps a moment from a fan who uses the feature on any device (`guide-moment` "Each guide moment is shown once per device").

### 2. A moment is a `guide-target` attribute plus one popover line

The target gets a `guide-target="<id>"` custom attribute that adds `data-guide-active` while `current` is that id; CSS draws the glow (an inner edge for the bubble field, a ring for buttons) and the motion, which `prefers-reduced-motion` turns into a steady glow. The line is a `popover="manual"` element anchored to the target with CSS Anchor Positioning (`position-anchor`, `position-try-fallbacks: flip-block`), shown after any open top-layer element so it sits above it without `z-index`, with `role="status"`. It takes no pointer events. A document-level `pointerdown` listener in the service ends the moment on any tap outside the target; route `detaching` ends it on leave.

`sheet.notify` is rendered inline instead, in the concert sheet's existing hint slot above the ticket section (`concert-sheet-hint`), because an element anchored from outside cannot sit inside the sheet's scrolling dialog. Alternative: the existing `coach-mark` — rejected; it dims the viewport and its spec keeps it Welcome-only.

### 3. Each screen requests its own moment

| moment | requested when | data read | acted |
|---|---|---|---|
| `discovery.follow` | the bubble field's first name reveal (the `first-name` reveal mark) and `followStore.followedCount === 0` | `FollowService.List` or the guest's follows on the device | first follow from a bubble or a search result |
| `discovery.swap` | artist bubbles attached, signed in, `onboarding.isCompleted`, and the device has never switched views | onboarding state and the view-swap mark on the device | swap tile tap (also sets the view-swap mark) |
| `concerts.filter` | the Concerts view's first load settles (list or empty state) | — | the action menu opens |
| `sheet.notify` | the concert sheet opens, not on Welcome, status is none or Lost, and the journey map is empty | `TicketJourneyService.List` (empty for a guest without a request) | notification button press |
| `myArtists.hype` | My Artists loaded, no home-area sheet open (or after `onHomeSheetHidden`), at least one follow, every hype is `nearby` | `FollowService.List` hype or the guest's follows | the first hype change |

Every value comes from data the screen already loads; no new RPC.

### 4. Guests see no swap tile and no Concerts view

`DiscoveryRoute` renders the swap tile only when signed in and resolves the view to the bubbles for a guest whatever the address says, rewriting `view=concerts` away with `replaceState`. The Timetable's empty-state 「ライブを探す」 link renders only when signed in. The Concerts view's guest branches (area override for a guest, guest follow → signup banner) become unreachable and are removed with their tests.

### 5. The guest 🔔 dialog reuses `confirm-dialog`

`confirm-dialog` already gives a native modal `<dialog>` (`showModal()`, focus trap, Escape and backdrop close) that enters the top layer above the open concert sheet. It gains a `cancelLabel` bindable (default 「キャンセル」) so this dialog reads 「あとで」, and the confirm label is 「Sign Up」. Focus starts on 「あとで」, the dialog's existing safe choice. Pressing 「Sign Up」 calls the existing `startTrackingSignUp()`. The guest push line (`concertSheet.pushLine.guest`) is removed.

### 6. A sign-up from 🔔 skips the celebration and asks for push after the sheet

The auth callback already knows the sign-up came from 🔔 (`resolveAuthTrackEventId(user)`). In that case it stores `postSignupShown = 'pending-track'` instead of `'pending'`. The Timetable then shows no celebration; when the deep-linked concert sheet closes it opens the post-signup dialog with a `variant="track"` that titles the notification step 「あとはプッシュ通知をオンにするだけ！」 and shows no body. The install step is unchanged. A sign-up from a Concert page keeps skipping both.

### 7. Help

`page-help` loses `auto-open` and its `onboarding.helpSeen:*` reads. Sections with a moment gain a 「チュートリアル」 button that closes the sheet and calls `replay(id)` after the sheet's `sheet-hidden`. Discovery's 「ライブ」 section renders for signed-in fans only.

### 8. The follow action moves into the sheet header

`concert-follow-cta` moves from the end of the concert sheet into its header row beside the artist name (a two-column grid: name `1fr`, button `auto`), with `discoveryConcerts.follow.action` = 「Follow」 and `.following` = 「Following」 in both locales.

### 9. Copy

| key | ja |
|---|---|
| new `guide.discoveryFollow` | 気になるアーティストをタップしてフォローしよう！ |
| new `guide.discoverySwap` | すぐに行けるライブも見てみよう！ |
| new `guide.concertsFilter` | 遠征するときはココを変更！ |
| new `guide.sheetNotify` | 気になるライブは見逃しNG！ |
| new `guide.myArtistsHype` | Hype (熱量) に合わせて 🔥 を変えてみよう！ |
| new `guide.replay` | チュートリアル |
| new `concertSheet.signUpDialog.{title,body,later,signUp}` | おっと、まだアカウントを持っていないね？ / 通知に必要なアカウントは無料ですぐに作成できるよ！ / あとで / Sign Up |
| new `actionMenu.concertsFilter` (the Timetable keeps `actionMenu.filter`) | エリアと期間を変える |
| new `postSignup.notify.titleTrack` | あとはプッシュ通知をオンにするだけ！ |
| `concertSheet.pushLine.guest` | removed |
| `hypeReach.signUp` | Sign Up |
| `discoveryConcerts.follow.action` / `.following` | Follow / Following |
| `timetable.celebration.chasing` | 新着ライブは\nLiverty Music にお任せ！ |
| `homeAreaSelector.title` | HOMEエリアを選択 |
| `homeAreaSelector.description` | 住んでるエリアを教えてね！近くのライブを HOME に並べるよ |
| `homeAreaSelector.saveFailed` | HOMEエリアを保存できませんでした。少し時間を置いてもう一度お試しください。 |
| `entity.homeArea.label`, `settings.myHomeArea` | HOMEエリア |
| `pageHelp.timetable.homeDesc` / `pageHelp.myArtists.homeDesc` | HOMEエリアのライブ / HOMEエリアのライブを通知 |
| `hypeReach.noHome` | HOMEエリア |
| `myArtists.signupBanner.message` | 新着ライブを通知で受け取ろう！ |

English values follow the spec scenarios. The Japanese copy was chosen by the owner; the English is a translation of it.

### 10. Analytics

`analytics-events.ts` gains `guide_shown`, `guide_acted` and `guide_dismissed` with `moment`, `is_guest`, `is_onboarding`, and `reason` (`other_tap`, `route_leave`, `blocked`) on dismissal; `blocked` means a sheet, dialog or celebration opened over a moment already shown, and a moment that waits behind a blocker sends nothing until it appears. With few users, PostHog session recordings confirm the timing.

## Risks / Trade-offs

- [A moment's popover appears under a sheet opened after it] → the service ends the current moment when a blocker opens.
- [Anchor Positioning missing on an old browser] → the line falls back to a fixed position above the bottom navigation; the glow still marks the target.
- [Seen marks are per device: a signed-in fan on a new device may see a moment again] → each screen's condition uses account data, so only `discovery.swap` and `concerts.filter` can repeat, once.
- [Hiding the Concerts view from guests removes an exploration path] → guests follow artists first; the Concerts view's follow and 🔔 already needed an account.

## Migration Plan

Frontend-only release. Old `onboarding.helpSeen:*` keys are left unread. Rollback is a revert.
