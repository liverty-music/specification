## Why

Nothing limits how much the prod project can spend on paid external APIs within a day. The place lookup API runs on its default daily limits: Text Search alone allows 75,000 requests per day, which at $32 per 1,000 is about ¥370,000 per day. Observed use is at most 588 requests per day (2026-05-30 to 2026-10-20). A bug that loops on a place lookup has already cost hundreds of thousands of yen once. The only cost guard today is an alerts-only budget, and it never stops anything.

## What Changes

- Lower the daily request limits of the place lookup API in prod to a little above observed use: Text Search 1,000 per day, Place Details 100 per day, Autocomplete 100 per day, and 0 for every method the backend does not call.
- Put a monthly spend cap of ¥4,000 on the generative AI API in prod. Once usage costs reach it, calls are paused until the next calendar month or a manual lift. The cap was already created on 2026-10-22 through the Cloud Billing Budget API, because the IaC tooling cannot express a spend cap yet (see design.md).
- Keep the project-wide alerts-only budget at ¥10,000 per month, unchanged.
- Correct the stale IaC comment that calls the project budget dormant. It has been live in prod since 2026-05-15.

## Capabilities

### New Capabilities
- `components/infrastructure/backend/process/paid-api-spend-cap`: the hard limits on paid external API use that every backend process in prod runs under, and how a call fails once a limit is reached.

### Modified Capabilities
(none)

## Impact

- cloud-provisioning: `src/gcp/index.ts` gains Cloud Quotas preferences for `places.googleapis.com` next to the existing Compute quota preferences. The stale budget comment is corrected.
- The prod billing account: a spend cap budget on the Gemini API for `liverty-music-prod` (created outside IaC; recorded in design.md).
- backend: no code change. Venue place lookups and concert or ticket-sale searches fail once a limit is reached; their callers already treat such failures as transient.
- dev: not touched (dev is stopped).
