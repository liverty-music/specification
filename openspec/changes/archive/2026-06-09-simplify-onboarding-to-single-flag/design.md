## Context

`OnboardingService` currently owns a 6-state linear machine (`LP → DISCOVERY → DASHBOARD → MY_ARTISTS → CONSENT → COMPLETED`) persisted to `localStorage['onboardingStep']`, plus ordinal navigation gating in `AuthHook`, a `readyForDashboard` predicate, and a discovery-count mirror (`setDiscoveryCounts`). A code audit (issue #444) showed the machine now causes more harm than value:

- The `MY_ARTISTS → CONSENT` transition is fired by a hype change in `onHypeInput`, which calls `setStep(CONSENT)` but never navigates. The second hype tap then hits the `isOnboarding` revert guard and is silently rolled back — the user-visible #444 bug.
- A pure guest never reaches `COMPLETED` (nothing navigates to the consent route, which is the only place `complete()` runs for guests), so `isOnboarding` stays `true` forever.
- The current code has regressed against the `my-artists` capability spec, which already mandates "hype change reverted during MY_ARTISTS step (REMOVED)".

A survey of all consumers shows the machine is really being used for only two things: (A) a first-run guidance phase, and (B) a "first run complete" flag. Everything else (`STEP_ORDER`, `STEP_ROUTE_MAP`, `stepIndex`, `normalizeStep`, the count mirror, the ordinal guard) is scaffolding for forced step ordering that the product no longer needs.

## Goals / Non-Goals

**Goals:**

- Collapse onboarding state to a single persisted boolean while keeping the public `isOnboarding` / `isCompleted` API stable so consumer call sites do not change.
- Fix #444 at the root by decoupling hype editing from onboarding progression.
- Keep the first-run coach mark as a delight beat, but as an independent UI service driven by live data rather than step transitions.
- Make the dashboard reachable at any time (soft gate), guiding empty guests with an empty-state CTA.
- Provide a one-time, lossless migration off the legacy `onboardingStep` key.

**Non-Goals:**

- Showing or redesigning the analytics consent screen. The `CONSENT` step is removed from the onboarding flow; consent *application* (fail-closed PostHog default, settings opt-out, `ConsentService`/`AnalyticsService`) is untouched and out of scope.
- Changing the discovery bubble UI, celebration visuals, page-help, or signup-banner behavior beyond their dependency on the retained `isOnboarding`/`isCompleted` getters.
- Reworking authentication gating in `AuthHook` (only the onboarding-ordering branches are removed).

## Decisions

### D1: Single boolean with retained getters, persisted as `onboardingComplete`

`OnboardingService` exposes `get isOnboarding()` and `get isCompleted()`; internally it holds one latched boolean and a single `finish()` mutator. The backing boolean MUST be `@observable` (Aurelia), because the getters are derived from it and consumers rely on change notification — `pwa-install-service` `@watch((vm) => vm.onboarding.isCompleted)`, the `app-shell.html` `if.bind` on `onboarding.isCompleted`, and the dashboard/my-artists `isOnboarding` template bindings. A plain field would leave these stale when `finish()` runs (PWA prompt never fires, banners/coach mark don't update). The **persisted** value uses completed-polarity (`onboardingComplete`, absent key = `false` = still onboarding), because localStorage absence naturally maps to falsy, and "not yet completed" is the correct default for a brand-new user. The **exposed** primary getter stays `isOnboarding = !onboardingComplete`.

- **Why over keeping the enum**: the enum's only load-bearing states were "in first run" and "done"; the ordered intermediate states existed solely to drive forced navigation, which we are removing.
- **Why retain `isCompleted`**: `notification-prompt`, `pwa-install-service`, and the dashboard signup banner read it; keeping it as `!isOnboarding` means zero churn at those call sites.

### D2: Completion latch = first dashboard arrival ∧ sign-up (B1 ∧ B2)

`finish()` is one-way. It is called from two idempotent sites:

- **B1 — first meaningful dashboard arrival**. The latch fires when the dashboard's timetable is real (region set and data loaded) **and** the guest has actually engaged (`followedCount >= 1`). It runs **after** the light-celebration decision (so `maybeCelebrate()` still observes `isOnboarding === true`) but is **independent of whether the celebration overlay is actually shown** — it must NOT be gated on the celebration firing. Two failure modes this avoids:
  - *Tying the latch to the celebration lifecycle* would strand any guest for whom the celebration is suppressed (`onboarding.celebrationShown === '1'` from a prior session, or any path that early-returns from `maybeCelebrate()`): `finish()` would never run and `isOnboarding` would stay `true` forever — re-creating the very "guest never completes" bug this change fixes. So the latch is driven by the *data-ready + engaged* condition, with the celebration merely sequenced ahead of it when it does show.
  - *Latching on a 0-follow dashboard arrival* (a brand-new guest deep-linking to `/dashboard`, allowed by the soft gate's empty state) would mark onboarding complete with no first-run done, suppressing the discovery coach mark and page-help auto-open thereafter. The `followedCount >= 1` gate prevents this; such a guest stays in onboarding until they follow an artist (then revisit dashboard) or sign up.
  - It must NOT be placed naively in `dashboard.attached()`, which fires before region selection / data load.
- **B2 — sign-up**, in `auth-callback`, as an idempotent backstop (covers users who sign up before a guest dashboard visit).

- **Alternative considered (B2 only)**: latch only on sign-up. Rejected — a pure guest would stay `isOnboarding === true` forever, so the dashboard signup banner (gated on `isCompleted && !auth`) would never appear, defeating conversion.

### D3: Soft gate via dashboard empty-state, not guard redirect (Option A)

`AuthHook` keeps auth gating, early-unlocked routes, and free roam, but drops the onboarding ordinal tree (`tutorialStep` comparison, `readyForDashboard`, step-route redirects, blocked-nav snackbars). A guest with no follows who lands on the dashboard sees an empty-state CTA pointing to discovery instead of being redirected.

- **Why over the ordered guard**: the guard's redirects only existed to enforce step order; removing the order removes the need. Empty-state guidance is the standard pattern and needs no state machine.

### D4: Coach mark extracted to `CoachMarkService`, triggered by live counts (decision 2b)

Spotlight state (`target`, `message`, `radius`, `active`, `onTap`) and `activate`/`deactivate` move from `OnboardingService` to a new `CoachMarkService`. `DiscoveryRoute` computes the trigger from its own live values: `isOnboarding && (followedCount >= DASHBOARD_FOLLOW_TARGET || artistsWithConcertsCount >= DASHBOARD_CONCERT_TARGET) && !shown`. `onTap` performs navigation only — it no longer advances any step. The targets move to a `constants` module.

- **Why extract rather than delete (2a)**: keeping the coach mark preserves the first-run delight, and moving it out is what lets `OnboardingService` become genuinely just a flag.
- **Why live counts over the mirror**: `DiscoveryRoute` already holds `followedCount` (live) and `artistsWithConcertsCount`; the `OnboardingService.setDiscoveryCounts` mirror was pure duplication of the follow-store source of truth.

### D5: Lossless one-time migration

On `OnboardingService` construction: if `localStorage['onboardingStep']` exists, set `onboardingComplete` to whether the legacy value denoted completion, persist under the new key, and delete the legacy key. "Denotes completion" MUST cover every legacy completed marker, not just the literal string `'completed'` — the deleted `STEP_MIGRATION` mapped the legacy numeric index `'7'` to `COMPLETED`, so a client still holding `onboardingStep === '7'` must migrate to `onboardingComplete = true`. Compare against the completed set `{'completed', '7'}` (inline, since `STEP_MIGRATION`/`normalizeStep` are deleted along with the enum). Any other value (including `'my-artists'`, `'discovery'`, `'detail'`, absent) maps to `false`.

## Risks / Trade-offs

- **Latch never fires when the celebration is suppressed** → drive `finish()` from the *data-ready + `followedCount >= 1`* condition, NOT from the celebration firing; the celebration is only sequenced ahead of it (D2). Covered by a test where `onboarding.celebrationShown === '1'` yet the latch still fires on a meaningful dashboard arrival.
- **Latch sequencing bug if placed in `attached()`** → evaluate after region selection / data load, honoring the `needsRegion` deferral, as in D2.
- **Stale reactivity** → the backing flag is `@observable` (D1); covered by a test asserting `pwa-install-service`'s `isCompleted` watcher and the `isOnboarding` bindings update when `finish()` runs.
- **Spec drift across six capabilities** → the `state-transition-diagram`, `frontend-route-guard`, and `onboarding-tutorial` specs encode the old machine. Each gets an explicit delta (MODIFIED/REMOVED) so the spec set stays the source of truth.
- **Losing the forced funnel reduces follow pressure** → accepted per Option A; the empty-state CTA plus the retained coach mark provide pull-based guidance. Revisit only if first-run follow conversion measurably drops.
- **Hidden `isOnboarding` consumers** → `onboarding-popover-guide`, `onboarding-page-help`, and `onboarding-celebration` all read `isOnboarding`/`isCompleted`; because both getters are retained with identical semantics for the two surviving states, these specs remain valid without a delta.

## Migration Plan

1. Land the single-flag `OnboardingService` with the construction-time legacy-key migration (D5).
2. Remove the enum/order/route-map and the `AuthHook` onboarding branches in the same change so no caller references deleted symbols.
3. Introduce `CoachMarkService` and repoint `DiscoveryRoute` / `app-shell` wiring.
4. Apply the #444 fix in `my-artists-route.ts`.
5. Wire `finish()` at the two latch sites (dashboard celebration lifecycle, auth-callback).
6. Rollback: revert the change set; the legacy key is already gone for migrated users, but `onboardingComplete` round-trips to the same two-state meaning, so a revert simply reinstates the old default-`LP` behavior for those users (worst case: they see the first-run guidance again).

## Open Questions

_None blocking._ Empty-state CTA copy/visual is a presentation detail to settle during implementation against the existing design system.
