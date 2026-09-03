## 1. Token layer (additive, no behavior change)

- [ ] 1.1 Add M3 spring motion tokens to `styles/tokens.css` — `--md-spring-spatial` `cubic-bezier(0.38,1.21,0.22,1)`/500ms, `--md-spring-spatial-fast` `cubic-bezier(0.42,1.67,0.21,0.9)`/350ms, `--md-spring-effects` `cubic-bezier(0.34,0.80,0.34,1)`/200ms (see design.md D4)
- [ ] 1.2 Add M3 role tokens mapped onto existing oklch brand values — `--md-color-primary-container`, `--md-color-on-primary-container`, `--md-color-menu-surface` (strong-contrast raised tier), `--md-color-scrim`; reuse `--shadow-card-glow` for FAB elevation (design.md D4/D8)
- [ ] 1.3 Add FAB layout tokens — `--fab-size` (56px), `--fab-inset` (`--space-s`), `--radius-full`→`--radius-card` morph endpoints, state-layer opacity values (hover 8% / focus 10% / pressed 10%) (design.md D4/D9)
- [ ] 1.4 Consult the official M3 FAB Menu docs and in-repo skills listed in design.md "M3 References" before finalizing values; reconcile any conflicts in favor of the official docs

## 2. FAB launcher primitive + service

- [ ] 2.1 Define `IFabMenuService` (`DI.createInterface` + `.singleton()`) with an `@observable actions` array, `register(owner, actions) → disposer` (owner-keyed idempotent replace), and a persisted `handed` ('right'|'left') property (design.md D1/D2/D6)
- [ ] 2.2 Add an `adapter/storage/` entry for the handedness preference (mirror the beam-preference pattern); no direct `localStorage` in the service
- [ ] 2.3 Define the `FabAction` type — `{ id, labelKey, icon, kind: 'command'|'toggle', isOn?, invoke }`
- [ ] 2.4 Create `components/fab-menu/` (`.ts` + `.html` + `.css`) — disclosure `<button aria-expanded aria-controls>` FAB + `popover="auto"` panel (`role="group"`), rendering each action as icon + label; toggle items carry `aria-pressed` (specs: labeled list, command/toggle, a11y)
- [ ] 2.5 Implement shape-morph + spring: `border-radius`+`scale` panel morph with `transform-origin` at the FAB corner, `+`↔`×` glyph rotate, item entrance stagger (`sibling-index()`/`:nth-child`), top-layer entry via `@starting-style` + `transition-behavior: allow-discrete` + `overlay`, animated `::backdrop` scrim (design.md D4)
- [ ] 2.6 Implement focus handling — move focus into the panel on open, return to the FAB on close; ensure Escape + light-dismiss close the panel (specs: accessibility contract)
- [ ] 2.7 Add `@media (prefers-reduced-motion: reduce)` fallback that lands the end state near-instantly (no overshoot, no stagger) (design.md D4)
- [ ] 2.8 Implement left/right placement via `fab-menu[data-handed]` logical-property swap bound to `fabMenu.handed` (design.md D6)
- [ ] 2.9 Enforce ≥48px item touch targets and M3 state layers (hover/focus/pressed/selected) on FAB and items (design.md D9)

## 3. Shell integration + nav offset

- [ ] 3.1 Mount a single `<fab-menu>` in `app-shell.html`, gated on `showNav && fabMenu.actions.length` (specs: app-shell hosts launcher; FAB hidden when nav hidden / zero actions)
- [ ] 3.2 Publish the bottom nav height as `--bottom-nav-height` on `bottom-nav-bar` `:scope`; FAB computes `inset-block-end = calc(var(--bottom-nav-height) + env(safe-area-inset-bottom) + var(--space-s))` (design.md D7)
- [ ] 3.3 Verify the FAB sits clear of the nav bar (no overlap) and drops the nav term when the nav is hidden

## 4. Relocate dashboard + page actions into the launcher

- [ ] 4.1 Dashboard: register `[beam, filter, mode-swap, help]` in `attached()` (My Timetable), `[mode-swap, help]` in All Nearby; re-register on `@watch('isAllNearby')`; dispose in `detaching()` (specs: per-route registration, no stale/duplicate; order per design.md D3)
- [ ] 4.2 Wire actions to existing surfaces — beam = inline `toggle` (`toggleBeams()` / `isOn: () => showBeams`), filter/help/mode = `command` (`filterBar.openSheet()`, `pageHelp.open()`, `toggleMode()`); command panels close the launcher as their sheet opens
- [ ] 4.3 Remove the beam toggle button, filter trigger, help `?` trigger, and mode-swap button from the dashboard `page-header` trailing slot; header becomes title-only
- [ ] 4.4 `page-help`: remove its own `?` trigger button, keep `open()`; register a `help` action on discovery / dashboard / my-artists (specs: help via launcher, no header `?`, no help item where no page help exists)
- [ ] 4.5 `artist-filter-bar`: remove its own trigger button, keep `openSheet()`; the sheet and its dashboard-owned bindings stay intact

## 5. Left-handed setting

- [ ] 5.1 Add a left-handed-mode toggle to `settings-route` bound to `fabMenu.handed`, persisted via the storage adapter (specs: persisted left-handed placement)

## 6. Tests + verification

- [ ] 6.1 Unit/component tests: `IFabMenuService` register/dispose + owner-keyed replace (no stale, no duplicate after navigate and after mode toggle)
- [ ] 6.2 Component tests: disclosure a11y (`aria-expanded`/`aria-controls`, no `role="menu"`), focus in/out, toggle `aria-pressed`, item = icon + label
- [ ] 6.3 `make lint` + `make test` green (Biome, stylelint, typecheck, brand-vocabulary)
- [ ] 6.4 Real-browser/device verification: thumb reach + nav offset (no overlap), spring/morph, `prefers-reduced-motion`, left-handed mirroring, beam toggle immediacy, filter/help sheet open with panel close, FAB hidden on fullscreen routes and where no actions exist
