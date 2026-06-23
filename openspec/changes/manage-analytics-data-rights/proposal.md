## Why

`introduce-analytics-tool` ships product analytics under an APPI EU-adequacy opt-out model: identified analytics is on by default, the user's `UserId` is the PostHog `distinct_id`, and behavioural data (events + session replay) is transferred to PostHog Cloud EU. Cross-border transfer is cleared by the EU adequacy designation, and the surviving notification/publication-of-purpose obligation is met by the privacy policy plus an always-available opt-out.

What is **not** yet handled is the other half of APPI's data-subject rights: a user's statutory right to **disclosure (開示)**, **correction (訂正)**, and **deletion / cessation of use (利用停止・消去)** of their personal data. Under the opt-out model these rights matter more, not less — because we collect by default, we must be able to honour a user's request to see, stop, and erase what we hold. Concretely, when a user deletes their account (or explicitly requests erasure), their PostHog profile keyed by `UserId` must be deleted too; today there is no code path that does this, so analytics data would outlive the account. This is a distinct concern from the collection design and is scoped as its own change to keep `introduce-analytics-tool` focused on instrumentation.

## What Changes

- Define an **analytics data-rights capability** covering the APPI rights as they apply to PostHog-held data: disclosure, correction, and deletion/stop-of-use, keyed on the platform `UserId`.
- On **account deletion**, erase the corresponding PostHog person and their events (PostHog person-deletion / GDPR-style erasure API) so analytics data does not outlive the account. Wire this into the existing account-deletion flow.
- Provide a path to honour a **standalone erasure / stop-of-use request** (without full account deletion): opt the user out, sever the identified profile, and delete the PostHog person on request.
- Provide a path to honour a **disclosure request**: assemble the categories of analytics data held for a given `UserId` (events, person properties, replays) for the response, within the APPI response window.
- Decide **where the request enters the system** (settings self-service vs. support-operator runbook vs. both) and the **SLA / audit-logging** for fulfilment.
- Define behaviour for **anonymous data**: anonymous-only profiles (never identified) carry no account linkage and are out of scope for per-user erasure; document this boundary.

## Capabilities

### New Capabilities

- `analytics-data-rights`: APPI disclosure / correction / deletion-and-stop-of-use for analytics data held in PostHog, keyed on `UserId`; account-deletion-triggered PostHog person erasure; standalone erasure/disclosure request handling; request intake, SLA, and audit logging; and the anonymous-data scope boundary.

### Modified Capabilities

- (Likely) the account-deletion flow / `identity-management` — to emit or invoke PostHog person-erasure as part of account deletion. To be confirmed during design once the deletion flow's owner is identified.

## Impact

- **New backend integration**: PostHog person-deletion / disclosure API calls (via the existing `posthog-go` dependency or PostHog's HTTP management API), invoked from the account-deletion path and from a request-fulfilment path.
- **Dependency on `introduce-analytics-tool`**: requires `distinct_id = UserId`, the `analytics-consumer`, and the opt-out model to be in place. This change is sequenced after it.
- **Operational**: a runbook for fulfilling disclosure/erasure requests within the APPI response window, plus audit logging of each fulfilment.
- **Out of scope**: the analytics collection design itself, the event catalogue, feature flags, and session-replay configuration (all owned by `introduce-analytics-tool`); general (non-analytics) APPI data-subject-rights tooling across the wider platform.

> Status: proposal only. Design, specs, and tasks are intentionally deferred until `introduce-analytics-tool` lands and the account-deletion flow owner is confirmed.
