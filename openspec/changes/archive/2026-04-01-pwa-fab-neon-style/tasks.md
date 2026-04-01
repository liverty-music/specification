## 1. CSS Changes

- [x] 1.1 Increase `.pwa-fab-icon` size from `1.25rem` to `1.5rem` in `frontend/src/components/pwa-install-fab/pwa-install-fab.css`
- [x] 1.2 Add `pwa-fab-neon-pulse` keyframe to `pwa-install-fab.css` using `--_glow-color-from` / `--_glow-color-to` tokens
- [x] 1.3 Replace the static `box-shadow` on `.pwa-fab` with comma-joined animation: `pwa-fab-enter 400ms ease-out both, pwa-fab-neon-pulse 2.5s ease-in-out 400ms infinite`
- [x] 1.4 Widen `outline-offset` on `&:focus-visible` from `3px` to `5px` and add `animation-play-state: paused`

## 2. Reduced Motion

- [x] 2.1 In the `prefers-reduced-motion: reduce` block, keep `animation: pwa-fab-fade ...` (which suppresses pulse) and add a static `box-shadow` fallback matching the `0%, 100%` keyframe values

## 3. Accessibility (HTML)

- [x] 3.1 In `pwa-install-fab.html`, change `aria-hidden.bind="isVisible ? 'false' : 'true'"` → `aria-hidden.bind="isVisible ? null : 'true'"`
- [x] 3.2 Add `tabindex.bind="isVisible ? '0' : '-1'"` to the button element

## 4. Spec Update

- [x] 4.1 Update `openspec/changes/pwa-fab-neon-style/specs/pwa-install-fab/spec.md` to add `aria-hidden` / `tabindex` control requirement

## 5. Verification

- [ ] 5.1 Confirm the icon is visibly larger in the FAB
- [ ] 5.2 Confirm the neon border pulses in idle state after the entry animation completes
- [ ] 5.3 Confirm the pulse pauses on keyboard focus (focus-visible outline is clearly readable)
- [ ] 5.4 Confirm the pulse is absent under `prefers-reduced-motion: reduce` and static box-shadow is shown
- [x] 5.5 Run `make lint` to verify no linting errors
