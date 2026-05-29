# Feature Flag Operational Policy

This document defines the operational policy for PostHog feature flags as implemented by the OpenSpec capability `feature-flag-management`. Every PostHog feature flag created against the Liverty Music project MUST follow this policy.

## When to create a flag

Feature flags are appropriate for:

- **Gradual rollout** of new features (10% → 50% → 100%).
- **A/B experiments** with a measurable hypothesis tied to a KPI (e.g. recommendation algorithm version vs. CTR).
- **Emergency kill switches** for features that may need to be turned off without a deploy (e.g. degraded ZK verification path).
- **Geographic gating** for features that launch in a subset of regions (e.g. metropolitan-Tokyo-only rollout).
- **Internal-only features** visible to staff cohorts in production (debug panels, ops tools).

Feature flags are NOT appropriate for:

- Button label changes or copy edits — deploy them.
- Bug fixes — deploy them.
- Refactors with no behaviour change — deploy them.
- "Just in case" hedging on features that have no rollback hypothesis — these become dead flags.

## Mandatory flag description template

Every flag's description in PostHog MUST contain the following block. Flags whose description omits any field are non-compliant and surfaced in the monthly review.

```
[OWNER] @<github-handle>
[HYPOTHESIS] <one-sentence assumption being tested or rollout reason>
[KPI] <event-name or metric the flag is expected to move>
[KILL_DATE] YYYY-MM-DD (creation date + 90 days)
[ISSUE] https://github.com/liverty-music/<repo>/issues/<n>
```

Example:

```
[OWNER] @pannpers
[HYPOTHESIS] Recommendation algorithm v2 increases artist.follow.completed by ≥ 10%
[KPI] artist.follow.completed / concert.recommendation.served
[KILL_DATE] 2026-08-27
[ISSUE] https://github.com/liverty-music/frontend/issues/123
```

## Evaluation rules

- **Significant experiments** (anything whose variant influences revenue, conversion, or per-user behaviour) MUST be evaluated only after `posthog.identify()` has completed. This defers experiment exposure to after identification, so analytics records only post-identification variant assignments; users in a treatment arm still see a deterministic, bounded control→treatment transition at the moment `identify` completes (matching the corresponding scenario in `specs/feature-flag-management/spec.md`), but variant churn for the rest of the session is eliminated.
- **Release toggles, geographic gates, and emergency kill switches** MAY be evaluated against the anonymous identifier when the variant difference is harmless to bucket flips (e.g. show or hide a landing-page section).
- **Default values are mandatory**. Every flag evaluation in frontend and backend code MUST specify a default that represents the safe, conservative behaviour. A CI check fails any evaluation lacking a default.

### Frontend evaluation

The frontend bootstraps flag values from `localStorage` on initialisation so that the first render uses the same variant the user saw on the previous session, then refreshes from PostHog asynchronously. The user-facing variant does not flip mid-session for returning users in the same identity state; for a first-session user a control→assigned-variant transition is permitted at the moment `posthog.identify()` completes (per the evaluation rule above) and at rollout-bucket boundaries.

### Backend evaluation

The backend uses PostHog's local-evaluation mode: flag definitions are synced periodically and evaluations happen in-process without blocking on PostHog availability. If sync has not completed at first use, the configured default is returned.

## Lifecycle and review

- **`KILL_DATE`** is creation date plus 90 days. Extending the date requires a documented justification.
- **Monthly review** runs on the first business day of each month. The review surfaces:
  - flags whose description omits any required field,
  - flags whose `KILL_DATE` has passed,
  - flags at 0% rollout for more than 30 days (candidates for removal),
  - flags at 100% rollout for more than 30 days (candidates for removal and code cleanup).
- The review produces a GitHub issue per flag requiring action, assigned to the `OWNER`.

## Flag removal

Removing a flag is a code change, not a PostHog operation:

1. Decide which variant becomes the permanent behaviour (almost always the rolled-out variant).
2. Remove the flag evaluation call and the unused code path from both frontend and backend in a single PR.
3. After the PR merges and the change is live in production, delete the flag from PostHog.
4. Close the originating GitHub issue.
