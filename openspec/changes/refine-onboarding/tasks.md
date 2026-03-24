## 1. Onboarding Step Entity — Remove DETAIL

- [ ] 1.1 Remove `OnboardingStep.DETAIL` from enum in `src/entities/onboarding.ts`
- [ ] 1.2 Remove `'detail'` from `STEP_ROUTE_MAP` in `onboarding.ts`
- [ ] 1.3 Add migration shim in `OnboardingStorage`: stored value `'detail'` reads back as `'dashboard'`
- [ ] 1.4 Remove all `isOnboardingStepDetail` computed properties and usages

## 2. Coach Mark — Remove router.load()

- [ ] 2.1 In `src/components/coach-mark/coach-mark.ts`, remove `router.load()` call from `onTargetClick` (keep `currentTarget.click()` and `onTap?.()`)
- [ ] 2.2 Verify nav tab taps through coach mark still navigate correctly via href

## 3. Discovery Route — Progression Condition + Coach Mark Fade

- [ ] 3.1 Update `showDashboardCoachMark` condition to: `followedCount >= 5 || artistsWithConcertsCount >= 3`
- [ ] 3.2 On condition first met: activate spotlight, set a 2-second timer to call `deactivateSpotlight()`
- [ ] 3.3 Ensure coach mark is not re-shown once already displayed this session (session flag)
- [ ] 3.4 Remove `discovery.popoverGuide` snack from `attached()` (replaced by PageHelp auto-open)

## 4. PageHelp Component — New Component

- [ ] 4.1 Create `src/components/page-help/page-help.ts` and `page-help.html` — persistent `?` icon button with `aria-label="ヘルプを表示"`
- [ ] 4.2 Accept bindable `page: 'discovery' | 'dashboard' | 'my-artists'` and `content: PageHelpContent`
- [ ] 4.3 On `attached()`: check `localStorage['liverty:onboarding:helpSeen:<page>']`; if not set and `onboarding.isOnboarding`, open bottom-sheet and set flag
- [ ] 4.4 On `?` tap: open bottom-sheet regardless of flag
- [ ] 4.5 Implement bottom-sheet content for Discovery: "アーティストをタップしてフォロー。フォロー解除は My Artists ページから" + follow progress count
- [ ] 4.6 Implement bottom-sheet content for Dashboard: HOME/NEAR/AWAY lane explanation + hype connection
- [ ] 4.7 Implement bottom-sheet content for My Artists: hype level table (👀/🔥/🔥🔥/🔥🔥🔥) + notification account note
- [ ] 4.8 Add i18n keys for all PageHelp content strings
- [ ] 4.9 Clear all `liverty:onboarding:helpSeen:*` keys in `GuestService.clearAll()` (called on fresh tutorial start)

## 5. Dashboard Route — Lane Intro Refactor

- [ ] 5.1 Remove `scheduleLaneIntroAdvance()` and 2-second `setTimeout` from `dashboard-route.ts`
- [ ] 5.2 Change each phase to advance only on tap callback (remove auto-timer)
- [ ] 5.3 Remove `'card'` phase from `laneIntroPhase` type; update all references
- [ ] 5.4 Implement `'waiting-for-home'` sub-state in HOME phase: open Home Selector inline, wait for `onHomeSelected`, then update coach mark text with selected prefecture name
- [ ] 5.5 Update HOME phase coach mark text: `"居住エリアのライブが並びます。居住エリアはどこですか？"` while waiting, `"{{prefecture}}のライブ"` after selection
- [ ] 5.6 Update NEAR phase coach mark text: `"少し足を伸ばせば行けるライブ"`
- [ ] 5.7 Update AWAY phase coach mark text: `"遠征ライブ！"`
- [ ] 5.8 Update i18n keys for Lane Intro phases (`dashboard.laneIntro.*`)
- [ ] 5.9 Move Home Selector trigger from `onCelebrationComplete` to `startLaneIntroHomePhase()`
- [ ] 5.10 Add nav tab dim logic: during Lane Intro phases, set `opacity: 0.3` + `aria-disabled="true"` on non-spotlight nav tabs
- [ ] 5.11 Restore nav tabs (full opacity, remove aria-disabled) when Lane Intro sequence ends

## 6. Dashboard Route — Card Tap + Celebration Reorder

- [ ] 6.1 Replace `onOnboardingCardTapped()` step-advance logic with `eventDetailSheet.open(concert)` call
- [ ] 6.2 Remove the My Artists spotlight activation that followed card tap
- [ ] 6.3 Move Celebration Overlay display to after Lane Intro AWAY phase completes (remove pre-lane-intro position)
- [ ] 6.4 In `celebration-overlay.ts`: remove `displayDuration` setTimeout; add click/pointerdown handler to fire completion callback on tap
- [ ] 6.5 Add secondary text to Celebration Overlay: `"自由にタイムテーブルを触ってみよう"`
- [ ] 6.6 On Celebration **open**: call `onboarding.setStep(MY_ARTISTS)` (DASHBOARD step completion trigger)
- [ ] 6.7 On Celebration **dismissed** (tap): deactivate blocker divs, release scroll lock, restore nav tabs
- [ ] 6.8 Update empty dashboard state: show dedicated empty-state UI instead of `skipToMyArtists()` (distinguish API error vs. zero concerts)

## 7. My Artists Route — Remove Revert + HypeNotificationDialog

- [ ] 7.1 Remove `artist.hype = prev` revert line from `onHypeInput()` in `my-artists-route.ts`
- [ ] 7.2 Remove `showNotificationDialog = true` trigger from `onHypeInput()`
- [ ] 7.3 Remove `HypeNotificationDialog` component import and element from `my-artists-route.html`
- [ ] 7.4 Keep `setStep(COMPLETED)` and `deactivateSpotlight()` on hype change during MY_ARTISTS step
- [ ] 7.5 Remove explicit `[data-artist-rows]` spotlight activation from `loading()` lifecycle
- [ ] 7.6 Add `PageHelp` component to `my-artists-route.html` (auto-opens on first visit)
- [ ] 7.7 Delete `src/components/hype-notification-dialog/` directory

## 8. Guest Service — Hype Storage

- [ ] 8.1 Add `hypes: Record<string, string>` to guest data structure in `GuestService`
- [ ] 8.2 Add `setHype(artistId: string, hype: string): void` method (writes to `liverty:guest:hypes`)
- [ ] 8.3 Add `getHypes(): Record<string, string>` method
- [ ] 8.4 Include `liverty:guest:hypes` in `clearAll()` cleanup
- [ ] 8.5 Call `guestService.setHype()` from `my-artists-route.ts` when guest changes hype

## 9. Auth Callback — Hype Merge + PostSignupDialog Trigger

- [ ] 9.1 In `auth-callback-route.ts` `provisionUser()`: after artist follow calls, call `FollowService.SetHype` for each entry in `guestService.getHypes()` (best-effort, log errors)
- [ ] 9.2 On first-time signup (new user path): set `localStorage['liverty:postSignup:shown']` to `'pending'` before navigating to `/dashboard`
- [ ] 9.3 In `dashboard-route.ts` `loading()`: check `localStorage['liverty:postSignup:shown'] === 'pending'`; if set, clear flag and set a flag to show `PostSignupDialog` after render

## 10. PostSignupDialog Component — New Component

- [ ] 10.1 Create `src/components/post-signup-dialog/post-signup-dialog.ts` and `.html`
- [ ] 10.2 Implement notification opt-in row: calls `PushService.subscribe()`, shows success/error state
- [ ] 10.3 Implement PWA install row: triggers deferred `beforeinstallprompt`; hides row if event unavailable
- [ ] 10.4 Implement `[あとで]` dismiss: closes dialog, notifies `IPromptCoordinator` that both prompts were deferred
- [ ] 10.5 Add `PostSignupDialog` to `dashboard-route.html` with conditional display

## 11. Welcome Page — Dashboard Preview

- [ ] 11.1 In `welcome-route.ts`: on `attached()`, fetch concert data for curated artist list (10–15 artists); collect results until ≥3 concerts available
- [ ] 11.2 Define curated artist ID list in a constants file (Mrs. GREEN APPLE, YOASOBI, Vaundy, Super Beaver, King Gnu, Official髭男dism, Ano, and others)
- [ ] 11.3 Embed read-only dashboard lane component in `welcome-route.html` using fetched data
- [ ] 11.4 Pass a `readonly` flag to disable card tap navigation in preview mode
- [ ] 11.5 Add "アカウント不要でお試しいただけます" copy to `welcome-route.html`
- [ ] 11.6 Add i18n key `welcome.guestFriendly` for the copy

## 12. Signup Prompt Banner — Copy Update

- [ ] 12.1 Update i18n key for signup banner copy to: `"アカウントを作成してフォロー情報を保存しよう。新着コンサート通知も有効になります！"`

## 13. Validation + Cleanup

- [ ] 13.1 Run `make lint` in frontend worktree; fix any issues
- [ ] 13.2 Run `make test` in frontend worktree; ensure existing tests pass
- [ ] 13.3 Update or remove E2E test `e2e/onboarding-flow.spec.ts` to reflect new step sequence and interactions
- [ ] 13.4 Verify `localStorage['liverty:onboardingStep'] = 'detail'` migration shim works correctly (manual test)
- [ ] 13.5 Verify guest hype values survive page reload and merge correctly after signup
