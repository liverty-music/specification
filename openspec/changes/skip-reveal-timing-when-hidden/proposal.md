## Why

`perf.discovery_reveal` measures a visit from the moment Discovery was opened, but the bubble field draws no frame while it is paused: while the page is hidden, in search mode and in the All Nearby view. When a fan switches away before every bubble shows a name, opens Discovery in a background tab, or opens it on the All Nearby view, the paused time is counted as time to reveal. Production has six such events (PostHog, 2026-10-18 to 2026-11-09): 96 s, 296 s, 396 s, 728 s, 4,458 s and 46,971 s to the first bubble, each followed by the names within 0–6 s. They do not move the medians, but they break any mean or high percentile of the reveal timings.

## What Changes

- A cold visit whose bubble field is paused before every bubble shows an artist name sends no reveal-timing event, for each cause of a pause the spec names (a hidden page, the All Nearby view, search mode), whether the field is paused when Discovery opens or during the reveal. It extends the existing rule that a fan who leaves Discovery before the reveal sends nothing, and matches the frame-timing event, which also leaves paused time out.
- The paused time is not subtracted. The network keeps working while the field is paused, so a time with the paused part removed is neither what the fan waited nor how fast the field loads.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/fan/web/route/discovery`: "Cold-load reveal timings are reported" no longer sends the event for a visit whose bubble field was paused before the reveal completed.

## Impact

- frontend: `src/routes/discovery/discovery-route.ts` starts the reveal timing only while the bubble field is shown, and drops it wherever it pauses the field; tests in `test/routes/discovery-route.spec.ts`.
- PostHog: fewer `perf.discovery_reveal` events; no property changes.
- No proto, backend or infrastructure change.
