## Why

Commit `e64f6e8` (2026-03-21) intended to remove the vertical grid lines between hype columns but accidentally also deleted the horizontal track line that connects hype dots. The track line is a spec requirement (`hype-inline-slider` spec: "4 dot stops connected by a 2px track line"). Additionally, the `passion-level` spec still lists the EN UI label for the Away tier as "Anywhere!" even though the `rename-hype-anywhere-to-away` change (2026-03-11) decided it should be "Away". The i18n implementation (`6155baa`) copied the stale spec label into `translation.json`.

## What Changes

- Restore the `::before` track line pseudo-element on `.hype-label` that was removed in `e64f6e8`, connecting all 4 hype dots with a 2px horizontal line
- Fix EN translation `myArtists.table.away` from "Anywhere!" to "Away"
- Update `hype-display.ts` `HYPE_TIERS` to use i18n keys instead of hardcoded Japanese strings
- Verify that vertical grid lines between hype columns are not visible (no CSS changes expected — the original removal was correct for borders; the visible lines may be cell-gap artifacts)

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `passion-level`: Fix EN UI label for Away tier from "Anywhere!" to "Away" (aligns spec with the `rename-hype-anywhere-to-away` decision)
- `hype-inline-slider`: No requirement change — restore implementation to match existing track line requirement

## Impact

- `frontend/src/routes/my-artists/my-artists-route.css` — restore track line CSS
- `frontend/src/locales/en/translation.json` — fix Away label
- `frontend/src/adapter/view/hype-display.ts` — replace hardcoded Japanese with i18n keys
- `specification/openspec/specs/passion-level/spec.md` — fix EN label in tier table
