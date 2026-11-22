## 1. specification: story map

- [x] 1.1 Write `docs/fan-story-map.md` in the shape of `docs/organizer-console-story-map.md`: the seven onboarding activities (知る, アーティストを集める, タイムテーブルを見る, チケットを逃さない, 熱量を伝える, 登録して通知を受け取る, 近くのライブを探す), the fan's steps, the existing interruptions, the five guide moments and where fans stop; verify every moment and interruption named in the specs of this change appears on it

## 2. frontend: guide moment surface (global/guide-moment; design Decisions 1, 2 and 10)

- [x] 2.1 Add `guide-storage.ts` (seen marks, view-swap mark) and `IGuideService` with `request`, `acted`, `dismiss`, `replay` and `current`, reading blockers from the bottom-sheet tracker and the prompt coordinator; verify unit tests for "One guide moment at a time, never over another interruption" (all three scenarios), "Each guide moment is shown once per device and survives sign-up" (all three) and "A guide moment ends when the fan acts or moves on" (both)
- [x] 2.2 Add the `guide-target` attribute and the guide line component (anchored manual popover, `role="status"`, steady glow under reduced motion); verify Storybook stories for a button target, the bubble-field edge and reduced motion, covering "A guide moment is a glow and one line that never blocks" (all four scenarios) with play functions that tap through the target and outside it
- [x] 2.3 Keep guide seen marks out of `clearOnboardingSeenFlags()`; verify a unit test for "Sign-up keeps seen moments"
- [x] 2.4 Send `guide.shown`, `guide.acted` and `guide.dismissed` from the service; verify a unit test for "Guide moments are reported"

## 3. frontend: Discovery (route/discovery; Decisions 3 and 4)

- [x] 3.1 Hide the swap tile from guests and resolve a guest's `view=concerts` to the artist bubbles with the address rewritten to `/discovery`; remove the Concerts view's guest-only branches and tests; verify unit tests for "A guest sees no swap tile", "A guest follows a link to the Concerts view", "Guest with no follows", "Area override for unauthenticated user", "Signed-in fan without a home area" and the reworded "Onboarding opens on the artist bubbles" and "Signing in, signing up or signing out clears the kept filter"
- [x] 3.2 Request `discovery.follow` on the first name reveal for a fan with no follow and act on the first follow (bubble or search); verify unit tests for "A new guest opens Discovery", "Follow from search", "A fan who already follows" and "Onboarding guidance overlay"
- [x] 3.3 Request `discovery.swap` for a signed-in fan with onboarding complete, at least one followed artist and no view-swap mark, act on the tile tap; verify unit tests for the four scenarios of "The swap tile's guide moment"
- [x] 3.4 Request `concerts.filter` when the Concerts view's first load settles, act when the action menu opens, and label the Concerts view's filter item with the new `actionMenu.concertsFilter`; verify unit tests for "The Concerts view's guide moment" (both scenarios) and "Filter item opens the filter sheet"
- [x] 3.5 Run Discovery in a local build with Playwright and mocked RPC: a guest with no follows sees the bubble-field moment and no swap tile; a signed-in fan with onboarding complete sees the swap-tile moment, taps it and sees the Concerts view moment; record screenshots at 412×915

## 4. frontend: concert sheet, guest dialog and Welcome (global/concert-sheet, global/bottom-sheet, route/welcome; Decisions 2, 5 and 8)

- [x] 4.1 Add `cancelLabel` to `confirm-dialog` and open it from a guest's notification press with the sign-up dialog copy; remove the guest push line; verify unit tests for "Guest presses the button", "Guest chooses Sign Up", "Guest chooses later", "No guest line in the ticket section" and a `confirm-dialog` story with a custom cancel label
- [x] 4.2 Show `sheet.notify` in the sheet's hint slot for a concert with no status when the journey map is empty, never on Welcome; verify unit tests for "First concert a guest opens", "Concert already tracked" and "Fan who tracks other concerts"
- [x] 4.3 Hide the notification button, push line and guide moment in Welcome's demo sheet; verify a unit test and the Welcome route story for "Card opens the real detail view"
- [x] 4.4 Move the follow action into the sheet header beside the artist name with 「Follow」 / 「Following」; verify concert-sheet stories at 320 px and 412 px for "Follow button visible for unfollowed artist in Concerts view context" and "Long artist name", and unit tests for "Follow action from detail sheet" and "Follow prompt for unauthenticated user"
- [x] 4.5 Change the out-of-range notice's guest action to 「Sign Up」; verify the existing out-of-range unit tests with the new label

## 5. frontend: sign-up from 🔔 (global/post-signup-dialog, global/celebration-overlay, stories/track-ticket-journey; Decision 6)

- [x] 5.1 Store `postSignupShown = 'pending-track'` in the auth callback when the sign-up carries a tracked event, skip the celebration for it, and open the post-signup dialog with the track variant when the concert sheet closes; verify unit tests for "Back from sign-up", "Closing the sheet", "Notifications already allowed", "Sign-up from the notification button" and the reworded "Title renders in Japanese locale" and "Dialog shown after first signup"
- [x] 5.2 Change the post-signup celebration's second line; verify the celebration-overlay unit test for "Post-signup full celebration then dialog"
- [x] 5.3 Extend `e2e/functional/ticket-notify-sign-up.spec.ts` with the dialog step and the return: "Guest signs up from the notification button", "Sign-up abandoned", "Guest chooses later" of stories/track-ticket-journey, plus no celebration overlay while and after the sheet is shown and the post-signup notification step after the sheet closes; verify it passes in the `functional` project

## 6. frontend: My Artists (route/my-artists; Decision 3)

- [x] 6.1 Request `myArtists.hype` after the home-area sheet (or at once without it) when every follow is at Nearby, light the first row's dots, act on the first hype change; verify unit tests for "A guest opens My Artists", "After the home-area sheet" and "A fan who set a level before"
- [x] 6.2 Change the hype snack's guest action to 「Sign Up」 and the no-home place word to 「HOMEエリア」; verify unit tests for "Guest picks Home" and "No home area"

## 7. frontend: help (global/page-help, global/coach-mark; Decision 7)

- [x] 7.1 Remove help auto-open and its seen flags, keep the hype snack flags' reset; verify unit tests for "Help never opens on its own", "Help-seen flags cleared on fresh onboarding", "Hype snack flags cleared at sign-up" and "Seen guide moments are kept at sign-up"
- [x] 7.2 Add 「チュートリアル」 to Discovery's two sections and My Artists' Hype section, show Discovery's 「ライブ」 section to signed-in fans only, and change the Hype table's Home row; verify unit tests for "Discovery help content", "My Artists help content", "Tier content per row", "Replay from Discovery help" and "Replay the hype moment"
- [x] 7.3 Confirm no coach mark and no dimming on Discovery, the Timetable and My Artists; verify the coach-mark unit test for "Only the Welcome demo shows a coach mark"

## 8. frontend: Timetable, banner and naming (route/timetable, global/signup-prompt-banner, global/home-area-selector, stories/find-concerts-nearby, stories/complete-onboarding)

- [x] 8.1 Show the empty state's 「ライブを探す」 to signed-in fans only; verify unit tests for "Guest with no follows", "Signed-in fan with no follows" and "Followed artists with nothing to show"
- [x] 8.2 Change the signup banner copy (ja, en); verify the banner stories at 320–412 px still fit on one line ("Message and button fit one line") and unit tests for both banner copy scenarios
- [x] 8.3 Rename the home area to HOMEエリア in every key of design Decision 9 and change the selector's title and description; verify unit tests for "Description copy explains what the HOME lane displays and asks for residence" and "One name for the home area" (a test that no ja value contains ホームエリア or 居住エリア)
- [x] 8.4 Update the find-concerts-nearby and complete-onboarding e2e specs for the guest and help changes; verify "A weekend near home", "No home area yet", "A guest", "Signed-in fan follows from a nearby concert", "Guest taps follow" and "No latch for a zero-follow timetable arrival" pass in the `functional` project

## 9. Release check

- [x] 9.1 After the release reaches prod, read-only: open the fan web as a new guest on the owner's Android phone, follow artists, open a concert and My Artists; confirm in PostHog that `guide.shown` arrived for `discovery.follow`, `sheet.notify` and `myArtists.hype` with `is_guest = true` (2026-11-21, v1.171.0 on prod: the owner ran it as a new guest on Android; PostHog has one `guide.shown` each for `discovery.follow` 20:35:43, `sheet.notify` 20:36:56 and `myArtists.hype` 20:37:14 JST, all `is_guest = true`, `$os = Android`)

## 10. specification: Purpose at archive

- [x] 10.1 At archive, edit the main specs' Purpose that the deltas cannot carry: page-help (help no longer auto-opens; guide moments point to features), find-concerts-nearby (a signed-in fan's goal) and the post-signup tier of celebration-overlay (not after a sign-up from 🔔); verify `openspec validate --specs` passes in the archive PR
