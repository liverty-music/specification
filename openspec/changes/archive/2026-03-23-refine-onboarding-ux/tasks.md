## Tasks

### Task 1: Fix bottom-sheet CSS selector for dismissable=false ✓

**Repo:** frontend
**Files:** `src/components/bottom-sheet/bottom-sheet.css`

Change the CSS selector from `:not([data-dismissable])` to `:not([data-dismissable="true"])` so that Aurelia's `data-dismissable="false"` output correctly disables dismiss-zone scroll-snap.

```css
/* Before */
.scroll-area:not([data-dismissable]) .dismiss-zone {

/* After */
.scroll-area:not([data-dismissable="true"]) .dismiss-zone {
```

**Verification:** Open the dashboard as a new onboarding user. After celebration overlay, the User Home Selector bottom sheet must be visible with its content at the bottom of the viewport.

---

### Task 2: Add semantic improvements to bottom-sheet ✓

**Repo:** frontend
**Files:** `src/components/bottom-sheet/bottom-sheet.html`, `src/components/bottom-sheet/bottom-sheet.ts`, `src/components/bottom-sheet/bottom-sheet.css`

- Change `.sheet-body` from `<div>` to `<section>`
- Add `host.setAttribute('role', 'dialog')` in `attached()`
- Update CSS selector from `.sheet-body` div references if any

---

### Task 3: Remove coach-mark tooltip solid background ✓

**Repo:** frontend
**Files:** `src/components/coach-mark/coach-mark.css`

Change `.coach-mark-tooltip`:
- `background: var(--color-surface-overlay)` → `background: transparent`
- `filter: drop-shadow(...)` → `filter: none`

**Verification:** Activate a coach mark spotlight. The tooltip text should float directly on the dark overlay without a visible background box.

---

### Task 4: Add language switcher to welcome page ✓

**Repo:** frontend
**Files:**
- `src/util/change-locale.ts` (new — shared utility)
- `src/routes/welcome/welcome-route.ts`
- `src/routes/welcome/welcome-route.html`
- `src/routes/welcome/welcome-route.css`
- `src/routes/settings/settings-route.ts` (refactor to use shared utility)
- `src/locales/ja/translation.json` (add keys if needed)
- `src/locales/en/translation.json` (add keys if needed)

1. Create `changeLocale(i18n, lang)` utility function
2. Refactor Settings to use the shared utility
3. Add language toggle buttons to welcome template (below Log In)
4. Style the toggle with the current language highlighted

---

### Task 5: Update bottom-sheet-ce spec ✓

**Repo:** specification
**Files:** `openspec/specs/bottom-sheet-ce/spec.md`

Merge the changes from `openspec/changes/refine-onboarding-ux/specs/bottom-sheet-ce.md` into the main spec. Update:
- DOM structure scenario (CE host popover, scroll-area, section.sheet-body)
- Non-dismissable scenario (CSS-controlled dismiss-zone snap)
- Remove `scrollTo` + `requestAnimationFrame` references
- Add initial-snap animation requirement

---

### Task 6: Update related specs ✓

**Repo:** specification
**Files:**
- `openspec/specs/onboarding-spotlight/spec.md`
- `openspec/specs/landing-page/spec.md`
- `openspec/specs/frontend-i18n/spec.md`

Merge the spec changes from this change's specs/ directory into the main specs.

---

### Task 7: Update bottom-sheet tests ✓

**Repo:** frontend
**Files:** `test/components/bottom-sheet.spec.ts`

Update or add test cases:
- Verify `role="dialog"` is set on host in `attached()`
- Verify that existing dismiss-zone DOM presence tests still pass (dismiss-zone remains in DOM for both true and false)
