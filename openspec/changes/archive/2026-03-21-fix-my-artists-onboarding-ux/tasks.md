## 1. Refactor HypeInlineSlider to Pure Presentation

- [x] 1.1 Remove `selectHype()` method, `isAuthenticated` bindable, `isOnboarding` bindable, and `INode` dependency from `hype-inline-slider.ts`
- [x] 1.2 Change `hype` bindable to `BindingMode.twoWay`
- [x] 1.3 Remove `click.trigger="selectHype(stop, $event)"` from `hype-inline-slider.html`

## 2. Move Business Logic to MyArtistsRoute

- [x] 2.1 Add `prevHypes: Map<string, Hype>` initialized in `loading()` after artist fetch
- [x] 2.2 Replace `onHypeChanged` + `onHypeSignupPrompt` with single `onHypeInput(artist)` handler: onboarding → revert + complete; unauthenticated → revert + dialog; authenticated → accept + RPC
- [x] 2.3 Update `my-artists-route.html`: replace `hype-changed.trigger` + `hype-signup-prompt.trigger` + `is-authenticated` + `is-onboarding` with `change.trigger="onHypeInput(artist)"`

## 3. Spotlight Target

- [x] 3.1 Change spotlight target from `'[data-hype-header]'` to `'[data-artist-rows]'` in `my-artists-route.ts`

## 4. Slider Track Vertical Centering

- [x] 4.1 Add `inset-block-start: 50%` and `translate: 0 -50%` to `.hype-slider-track` in `hype-inline-slider.css`

## 5. Default Hype Level

- [x] 5.1 Change guest follow default from `'away' as const` to `'watch' as const` in `follow-service-client.ts`

## 6. Track Line Containing Block Fix

- [x] 6.1 Move `::before` from `.hype-col` (`<td>`) to `.hype-col:first-of-type .hype-label::before` in `my-artists-route.css`
- [x] 6.2 Remove `position: relative` from `.hype-col`; ensure `.hype-label` has `position: relative; display: flex`
- [x] 6.3 Add `pointer-events: none` to track line pseudo-element

## 7. Unauthenticated Loading Guard

- [x] 7.1 Add early return in `loading()` for `!this.isAuthenticated` — skip `ListFollowed` RPC
- [x] 7.2 Activate spotlight for `isOnboardingStepMyArtists` within the early return path

## 8. First-Tap Notification Dialog

- [x] 8.1 In `onHypeInput()` onboarding complete branch: open notification dialog for unauthenticated users on the same tap (before `return`)

## 9. Tests

- [x] 9.1 Update `my-artists-route.spec.ts`: spotlight target, `onHypeInput` handler tests (onboarding / unauthenticated / authenticated branches)
- [x] 9.2 Fix unauthenticated user tests: tests already work — `beforeEach` loads while authenticated then switches to unauth
- [x] 9.3 Run `make check` — lint clean, 845 unit tests pass

## 10. Manual Verification

- [ ] 10.1 Onboarding Step 5: tap hype dot → onboarding completes → notification dialog opens immediately
- [ ] 10.2 Guest (post-onboarding): tap hype dot → slider reverts, signup dialog appears
- [ ] 10.3 Authenticated: tap hype dot → slider moves, RPC fires
- [ ] 10.4 Track line spans exactly from first to last dot, not into unfollow column
