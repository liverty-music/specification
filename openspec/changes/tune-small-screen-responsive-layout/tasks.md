## 1. CSS: Discovery search bar vertical compression

- [ ] 1.1 In `src/routes/discovery/discovery-route.css`, add `@media (height <= 700px)` block that sets `.search-bar` `padding-block` to `var(--space-3xs)` and `margin-block-start` to `var(--space-3xs)`
- [ ] 1.2 Confirm search bar renders ~8px shorter per side at 375×667 viewport in browser DevTools

## 2. CSS: Page header vertical compression

- [ ] 2.1 In `src/components/page-header/page-header.css`, add `@media (height <= 700px)` block that sets `.page-header` `padding-block` to `var(--space-2xs)`
- [ ] 2.2 Confirm header row is visibly more compact on 375×667 viewport without breaking the title or slot actions layout

## 3. CSS: Coach mark tooltip overflow fix

- [ ] 3.1 In `src/components/coach-mark/coach-mark.css`, change `.coach-tip` `max-inline-size` from `320px` to `min(320px, calc(100dvw - 2 * var(--space-s)))`
- [ ] 3.2 Verify tooltip does not overflow on a 320px-wide viewport in DevTools

## 4. TypeScript: Bubble count cap on narrow canvases

- [ ] 4.1 In `src/components/dna-orb/dna-orb-canvas.ts`, derive a `displayLimit` constant inside (or just after) `resize()` using the existing `rect.width`: `Math.min(artists.length, rect.width < 390 ? 30 : 50)`
- [ ] 4.2 Apply `displayLimit` when passing artists to the physics initializer so that only that many bubbles are spawned
- [ ] 4.3 Confirm that at 375px canvas width, no more than 30 bubbles are rendered; at 390px+, up to 50 are rendered

## 5. TypeScript: DNA Orb radius cap on narrow canvases

- [ ] 5.1 In `src/components/dna-orb/stage-effects.ts`, introduce a `effectiveMaxRadius` variable that is `Math.min(MAX_RADIUS, canvasWidth < 390 ? 70 : MAX_RADIUS)` and apply it in `getStageParams` when computing `orbRadius`
- [ ] 5.2 Thread `canvasWidth` into `getStageParams` (or pass `effectiveMaxRadius` from the call site in `dna-orb-canvas.ts`)
- [ ] 5.3 Confirm at 375px canvas width that the orb diameter does not exceed 140px

## 6. Verification

- [ ] 6.1 Open Discovery page in Chrome DevTools at iPhone SE (375×667) — verify bubbles are fewer and not visually crowded, search bar is slimmer, orb is proportionate
- [ ] 6.2 Open Discovery page at 390×844 (iPhone 14 baseline) — verify no visual regression (full 50 bubbles, full orb radius)
- [ ] 6.3 Open coach mark at 320px width — verify tooltip stays within the viewport
- [ ] 6.4 Run `make check` in frontend and confirm zero type errors and lint failures

## 7. Specification sync and release

- [ ] 7.1 Open PR in frontend with all changes and pass CI
- [ ] 7.2 Sync delta spec to main spec (`openspec sync-specs` or manual merge of `artist-discovery-dna-orb-ui`)
- [ ] 7.3 Open specification PR for the delta-to-main sync
- [ ] 7.4 Merge frontend PR and create a patch release
- [ ] 7.5 Merge specification PR
