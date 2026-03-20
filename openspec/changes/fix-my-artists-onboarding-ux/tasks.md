## 1. Refactor HypeInlineSlider to Pure Presentation

- [x] 1.1 Remove `selectHype()` method, `isAuthenticated` bindable, `isOnboarding` bindable, and `INode` dependency from `hype-inline-slider.ts`
- [x] 1.2 Change `hype` bindable to `BindingMode.twoWay`
- [x] 1.3 Remove `click.trigger="selectHype(stop, $event)"` from `hype-inline-slider.html`

## 2. Move Business Logic to MyArtistsRoute

- [x] 2.1 Add `prevHypes: Map<string, Hype>` initialized in `loading()` after artist fetch
- [x] 2.2 Replace `onHypeChanged` + `onHypeSignupPrompt` with single `onHypeInput(artist)` handler: onboarding → revert + complete; unauthenticated → revert + dialog; authenticated → accept + RPC
- [x] 2.3 Update `my-artists-route.html`: replace `hype-changed.trigger` + `hype-signup-prompt.trigger` + `is-authenticated` + `is-onboarding` with `change.trigger="onHypeInput(artist)"`

## 3. Spotlight Target

- [x] 3.1 Change spotlight target from `'[data-hype-header]'` to `'.artist-list'` in `my-artists-route.ts`

## 4. Slider Track Vertical Centering

- [x] 4.1 Add `inset-block-start: 50%` and `translate: 0 -50%` to `.hype-slider-track` in `hype-inline-slider.css`

## 5. Default Hype Level

- [x] 5.1 Change guest follow default from `'away' as const` to `'watch' as const` in `follow-service-client.ts`

## 6. Tests

- [x] 6.1 Update `my-artists-route.spec.ts`: spotlight target, `onHypeInput` handler tests (onboarding / unauthenticated / authenticated branches)
- [x] 6.2 Run `make check` — all pass

## 7. Manual Verification

- [ ] 7.1 Onboarding Step 5: tap hype dot → onboarding completes → redirect to LP
- [ ] 7.2 Guest (post-onboarding): tap hype dot → slider reverts, signup dialog appears
- [ ] 7.3 Authenticated: tap hype dot → slider moves, RPC fires
