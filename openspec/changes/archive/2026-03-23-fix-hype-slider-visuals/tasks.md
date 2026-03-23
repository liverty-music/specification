## 1. Restore hype dot track line

- [x] 1.1 In `frontend/src/routes/my-artists/my-artists-route.css`, restore the `::before` pseudo-element inside `.hype-label` (after `min-block-size: 44px`) that was removed in `e64f6e8`:
  ```css
  .hype-col:first-of-type > &::before {
      content: "";
      pointer-events: none;
      position: absolute;
      inset-block-start: 50%;
      inset-inline-start: 50%;
      translate: 0 -50%;
      inline-size: calc(3 * 100%);
      block-size: 2px;
      background: var(--color-border-subtle, oklch(100% 0 0deg / 10%));
  }
  ```

## 2. Fix EN "Anywhere!" label

- [x] 2.1 In `frontend/src/locales/en/translation.json`, change `myArtists.table.away` from `"Anywhere!"` to `"Away"`
- [x] 2.2 In `frontend/src/adapter/view/hype-display.ts`, replace hardcoded Japanese `labelKey` values with i18n keys: `watch` → `myArtists.table.watch`, `home` → `myArtists.table.home`, `nearby` → `myArtists.table.nearby`, `away` → `myArtists.table.away`

## 3. Update spec

- [x] 3.1 In `specification/openspec/specs/passion-level/spec.md`, update the tier table EN label from "Anywhere!" to "Away" and "Just checking" to "Watch"

## 4. Verify

- [x] 4.1 Run `make check` in frontend to ensure lint and tests pass
- [x] 4.2 Visual verification with Playwright: navigate to `/my-artists`, confirm track line is visible connecting dots, confirm no vertical grid lines between columns, confirm Away column header reads "Away" (not "Anywhere!")
