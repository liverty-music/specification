## Why

Gemini grounding (Google Search) queries are the main cost of concert discovery: in 2026-09 they were 78% of the Gemini bill, and the project hit its monthly spend cap on 09-05. The current Step 1 prompt passes only the official site's host (so URL context cannot fetch it) and asks for exhaustive discovery; a controlled evaluation on gemini-3.8-flash cut search queries from 55 per call to roughly 14–39 with equal or better recall. The same evaluation found two silent-failure paths: responses with no candidates are treated as "nothing new" and suppress the next search, and overseas venues lose their admin area.

## What Changes

- Concert discovery calls gemini-3.8-flash with thinking `low` and no temperature, a short system instruction (scope, sources, output contract only), the official site's full URL, and a Google Search time range of the last 2 months.
- The grounded call returns the final events as structured JSON; the separate parse call (Step 2, flash-lite) and the XML envelope are removed.
- Admin areas are returned as ISO 3166-2 codes for venues in any country, not only Japan's 47 prefectures.
- Venue names are kept as printed, including former-name annotations (e.g. 「クロコくんホール（旧 日本ガイシホール）」); notation variants across official pages (full/half-width, compatibility characters, spacing) no longer split one venue when removing repeats.
- A response with no candidates fails the search instead of returning no concerts, so the Artist's SearchLog becomes failed and the next daily run searches again. It is not retried within the same search.
- Each Gemini response log includes the search queries the model ran, alongside the existing token and finish metadata.
- Prod reuses a completed search for 96h instead of 72h (configuration).
- The suspended prod `concert-discovery` CronJob is resumed after rollout; `sales-phase-discovery` stays suspended.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/entity/concert/search`: admin area accepts any ISO 3166-2 subdivision; venue text keeps annotations and notation variants are folded when removing repeats; a response with no candidates fails Search with an error instead of degrading to no results.

`components/usecase/concert/search-new-concerts` is unchanged: its existing requirement already marks the SearchLog failed when the external search fails and searches a failed Artist on the next run, and the freshness window is already configurable per environment. The Venue and DiscoveredSeries entities already define admin area as any ISO 3166-2 code, so they are unchanged.

## Impact

- backend: `internal/infrastructure/gcp/gemini` (searcher prompt, request config, single-step JSON schema and parsing, empty-candidate error, response logging, venue normalization), `internal/infrastructure/geo` (ISO 3166-2 pass-through), `pkg/config` model defaults, DI wiring for the new searcher options.
- cloud-provisioning: prod `concert-discovery` ConfigMap (model, thinking, cache TTL 96h) and removal of its suspend patch; `sales-phase-discovery` suspend stays.
- Gemini API: structured output combined with built-in tools and `include_server_side_tool_invocations` are Preview features.
- The A/B harness and fixtures already on the backend branch `test/refresh-vaundy-ab-fixture` carry the evaluation; they are test-only.
