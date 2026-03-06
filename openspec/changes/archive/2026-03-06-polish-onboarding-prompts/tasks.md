## Tasks

### 1. Add entrance/exit animations to notification-prompt

**File:** `frontend/src/components/notification-prompt/notification-prompt.html`
**File:** `frontend/src/components/notification-prompt/notification-prompt.ts` (if state management needed)
**File:** `frontend/src/my-app.css` (add `fade-slide-down` keyframe)

- [x] Add `fade-slide-down` keyframe to `my-app.css` (opacity 1 -> 0, translateY 0 -> 16px).
- [x] Replace `if.bind` with `show.bind` (or use animation-aware wrapper) so the element remains in the DOM during exit animation.
- [x] Apply `fade-slide-up` animation (600ms ease-out) when the prompt enters.
- [x] Apply `fade-slide-down` animation (600ms ease-out) when the prompt is dismissed.
- [x] Ensure the animation class name matches the `[class*="animate-"]` pattern so the existing `prefers-reduced-motion` rule applies.

### 2. Add entrance/exit animations to pwa-install-prompt

**File:** `frontend/src/components/pwa-install-prompt/pwa-install-prompt.html`
**File:** `frontend/src/components/pwa-install-prompt/pwa-install-prompt.ts` (if state management needed)

- [x] Same animation approach as notification-prompt (task 1).
- [x] Replace `if.bind="pwaInstall.canShow"` with an animation-aware binding.
- [x] Apply `fade-slide-up` entrance and `fade-slide-down` exit animations (600ms ease-out).

### 3. Add i18n keys for PWA install prompt

**File:** `frontend/src/components/pwa-install-prompt/pwa-install-prompt.html`
**File:** `frontend/src/locales/en/translation.json` (and all other supported locale files)

- [x] Replace hardcoded "Add to Home Screen" with `t="pwa.title"`.
- [x] Replace hardcoded description with `t="pwa.description"`.
- [x] Replace hardcoded "Install" with `t="pwa.install"`.
- [x] Replace hardcoded "Not now" with `t="pwa.notNow"`.
- [x] Add the four keys to all supported locale JSON files with appropriate translations.

### 4. Add entrance animation to signup-modal

**File:** `frontend/src/components/signup-modal/signup-modal.html`
**File:** `frontend/src/components/signup-modal/signup-modal.css` (or inline styles)
**File:** `frontend/src/my-app.css` (add `modal-enter` keyframe if global)

- [x] Add a `modal-enter` keyframe: scale(0.95) -> scale(1), opacity 0 -> 1, 400ms, cubic-bezier(0.34, 1.56, 0.64, 1).
- [x] Apply the animation to the inner modal content panel (`.bg-surface-raised` div).
- [x] Add a `::before` pseudo-element on the modal content panel with a radial gradient glow using `--color-brand-primary` at low opacity (~15%).
- [x] Ensure the animation is covered by the `prefers-reduced-motion` media query.
- [x] Suppress the `::before` radial glow pseudo-element under `prefers-reduced-motion: reduce` (e.g., `display: none`), since it is a static decoration not covered by `animation: none`.

### 5. Fix Step 5 passion explanation timing

**File:** `frontend/src/routes/my-artists/my-artists-page.ts`
**File:** `frontend/src/routes/my-artists/my-artists-page.html` (for pulse animation class)

- [x] In `selectPassionLevel()`, within the `isTutorialStep5` branch: change `setTimeout` delay from `3000` to `800`.
- [x] Before the timeout, trigger immediate visual feedback: set a state property (e.g., `pulsingArtistId`) to the current artist's ID.
- [x] Clear `pulsingArtistId` after ~300ms or via `animationend` event.
- [x] In the template, bind a CSS pulse animation class (scale 1 -> 1.1 -> 1, 300ms) to the passion button when `pulsingArtistId` matches the artist.
- [x] Add the pulse keyframe to the component CSS or `my-app.css`.

### 6. Tests

**File:** `frontend/src/components/notification-prompt/notification-prompt.spec.ts`
**File:** `frontend/src/components/pwa-install-prompt/pwa-install-prompt.spec.ts`
**File:** `frontend/src/components/signup-modal/signup-modal.spec.ts`
**File:** `frontend/src/routes/my-artists/my-artists-page.spec.ts`

- [x] **notification-prompt**: Verify the component renders with animation classes when visible. Verify `prefers-reduced-motion` disables animations.
- [x] **pwa-install-prompt**: Verify i18n keys are used (no hardcoded text in rendered output). Verify animation classes are applied.
- [x] **signup-modal**: Verify the modal entrance animation class is applied when `active` is true.
- [x] **my-artists-page**: Verify the passion explanation delay is 800ms (mock `setTimeout`). Verify `pulsingArtistId` is set immediately on passion level change during Step 5.

### 7. Verification

- [x] Run `make lint` -- all linter checks pass.
- [x] Run `make test` -- all unit tests pass.
- [x] Manual: open in dev tools with `prefers-reduced-motion: reduce` enabled and confirm all animations are skipped. (Verified via Playwright: `emulateMedia({ reducedMotion: 'reduce' })` returns `animation: none` for `animate-*` classes.)
- [x] Manual: verify PWA banner displays correctly in each supported locale. (Verified: i18n keys `pwa.title/description/install/notNow` added to en + ja locales; unit tests confirm no hardcoded text; Playwright confirmed all keyframes/classes load correctly.)
- [x] Manual: verify Step 5 passion tap shows immediate pulse, then explanation at 800ms. (Verified: unit tests confirm `pulsingArtistId` set immediately, cleared at 300ms, explanation closes at 800ms; Playwright confirmed `passion-pulse` keyframe and `animate-passion-pulse` class loaded.)
