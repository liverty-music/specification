## Context

The My Artists hype slider originally rendered a 2px horizontal track line connecting all 4 dots using a `::before` pseudo-element on `.hype-label` scoped to `.hype-col:first-of-type`. Commit `e64f6e8` removed this CSS block while targeting vertical grid lines, breaking the visual connection between dots. The `hype-inline-slider` spec explicitly requires "4 dot stops connected by a 2px track line".

Separately, the `passion-level` spec's EN UI label for the Away tier was never updated from "Anywhere!" to "Away" after the `rename-hype-anywhere-to-away` change. The i18n implementation propagated this stale label.

## Goals / Non-Goals

**Goals:**
- Restore the horizontal track line connecting hype dots
- Fix EN "Anywhere!" → "Away" in translation and spec
- Replace hardcoded Japanese in `hype-display.ts` with i18n keys

**Non-Goals:**
- Redesigning the slider visual style
- Changing the track line's appearance (color, width, position)
- Investigating vertical grid line artifacts (current CSS has no explicit vertical borders)

## Decisions

### 1. Restore track line CSS with restructured nesting

**Choice**: Re-insert the `::before` pseudo-element for the track line, but nest it inside `.hype-col` (not `.hype-label` as in the original) to avoid a browser limitation with `@scope` + CSS nesting.

Original (before `e64f6e8`, nested inside `.hype-label`):
```css
.hype-col:first-of-type > &::before { ... }
```

Actual implementation (nested inside `.hype-col`):
```css
&:first-of-type > .hype-label::before { ... }
```

Both resolve to the same selector: `.hype-col:first-of-type > .hype-label::before`. However, when `&` refers to `.hype-label` and appears mid-selector inside `@scope`, Chromium silently drops the rule. Moving the nesting anchor to `.hype-col` (where `&` is at the start) avoids this.

**Why**: The original CSS properties (position, dimensions, background) are unchanged — only the nesting structure differs. Verified visually with Playwright.

### 2. Fix EN label to "Away" (not "Anywhere")

**Choice**: Update `translation.json` EN `myArtists.table.away` to "Away" and update `passion-level/spec.md` tier table EN label to "Away".

**Why**: The `rename-hype-anywhere-to-away` change (2026-03-11) established "Away" as the canonical EN label. The spec was not updated, causing the i18n implementation to use the stale "Anywhere!" label.

### 3. Replace hardcoded Japanese in hype-display.ts with i18n keys

**Choice**: Change `HYPE_TIERS` `labelKey` values from hardcoded Japanese strings to i18n translation keys (`myArtists.table.watch`, etc.).

**Why**: The file was missed during the i18n migration in `6155baa`. Using keys ensures labels respect the user's locale setting.

## Risks / Trade-offs

- **hype-display.ts consumers**: Any code using `HYPE_TIERS[tier].labelKey` as a display string will now get an i18n key instead. Verified: the only consumer (`trHypeLabel`) was dead code and has been removed.
