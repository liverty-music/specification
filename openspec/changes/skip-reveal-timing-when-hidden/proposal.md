## Why

`perf.discovery_reveal` measures a page-load visit from the start of the page load, but the canvas draws no frame while the page is hidden. When a fan opens the app and switches away before every bubble shows a name, or opens Discovery in a background tab, the hidden time is counted as time to reveal. Production has six such events (PostHog, 2026-10-18 to 2026-11-09): 96 s, 296 s, 396 s, 728 s, 4,458 s and 46,971 s to the first bubble, each followed by the names within 0–6 s. They do not move the medians, but they break any mean or high percentile of the reveal timings.

## What Changes

- A cold visit whose page is hidden before every bubble shows an artist name sends no reveal-timing event. This covers a page hidden when Discovery opens and a page hidden during the reveal. It extends the existing rule that a fan who leaves Discovery before the reveal sends nothing.
- The hidden time is not subtracted. The network keeps working while the page is hidden, so a time with the hidden part removed is neither what the fan waited nor how fast the field loads.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/discovery`: "Cold-load reveal timings are reported" no longer sends the event for a visit whose page was hidden before the reveal completed.

## Impact

- frontend: `src/routes/discovery/discovery-route.ts` starts the reveal timing only while the page is visible and drops it when the page is hidden; a test in `test/routes/discovery-route.spec.ts`.
- PostHog: fewer `perf.discovery_reveal` events; no property changes.
- No proto, backend or infrastructure change.
