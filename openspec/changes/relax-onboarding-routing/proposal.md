## Why

Onboarding currently rails the user through a strictly forward, hard-gated navigation flow whose blocks are **silent** — tapping a locked bottom-nav tab during onboarding does nothing, with no explanation. There is no way back to the Welcome page, no login entry point once onboarding starts (trapping returning users who mis-tap "Get Started"), and the only "celebration" payoff component was orphaned when the Lane Intro sequence was removed. Meanwhile several canonical specs still describe that removed Lane Intro / Celebration machinery, so the spec set no longer matches the implementation. This change relaxes the navigation restrictions toward a soft-gated, free-roam model (modern guest-mode UX), restores the celebration as a deliberate two-tier emotional payoff, and re-aligns the drifted specs with reality.

## What Changes

**A. Navigation guard relaxation**
- Replace every **silent** redirect in the route guard with explicit feedback (a contextual snackbar, e.g. "あと N 組フォローでタイムテーブルが見られます", or a re-lit coach mark). No guard-blocked navigation is a no-op.
- Make the **Settings** route reachable from the `discovery` step onward (currently blocked until much later).
- Make **Settings guest-adaptive**: the ACCOUNT section renders a sign-in / sign-up CTA for guests and **hides** email-verification + sign-out; language selection and home-area work for guests.
- After dashboard, open **all** navigation (tickets, settings) for guests — features that require an account are **hidden at point of use, not navigation-blocked**.
- Allow returning to the **Welcome** page during onboarding.
- Move the onboarding-completion trigger from "user changes a hype level on My Artists" to "user **arrives** at My Artists" (`.attached()`), so completion (and the signup banner / free-roam) no longer requires an action. Unfollow is consequently released on arrival. **BREAKING** (behavioral): completion no longer requires a hype change.

**B. Celebration revival (two-tier)**
- Revive the orphaned `celebration-overlay`, decoupled from the removed Lane Intro.
- Add a `confetti` flag; fire via a single `maybeCelebrate()` gated on home-selector completion + timetable render, once per session.
- Tier Z-light = guest's first dashboard (no confetti); tier Z-full = post-signup redirect (confetti) → then PostSignupDialog (emotion → setup).

**C. Spec drift cleanup (align specs with the post-Lane-Intro implementation)**
- Delete the vestigial `nav-dimming-service` (only ever undimmed).
- Remove the `dashboard-lane-introduction` capability (Lane Intro no longer exists).
- Rewrite/trim Lane-Intro / Celebration / nav-dimming references out of the onboarding specs and correct the state-transition diagram.

## Capabilities

### New Capabilities
- `guest-mode-access`: The cross-cutting policy for an unauthenticated guest — which routes a guest may navigate (free roam after dashboard), the principle that account-only features are **hidden** rather than navigation-blocked, and the persistent auth-entry affordance available from the discovery step onward.

### Modified Capabilities
- `frontend-route-guard`: Replace silent redirects with feedback; allow Settings from the discovery step; allow Welcome return during onboarding; remove the COMPLETED-guest hard block on tickets/settings in favor of free roam with point-of-use hiding.
- `settings`: Guest-adaptive Settings — early access during onboarding; ACCOUNT section conditional on auth state (guest CTA vs email-verification + sign-out); language change usable by guests (no backend persistence); home-area sourced from guest storage for guests.
- `frontend-onboarding-flow`: Move completion trigger from hype-change to My Artists arrival; remove stale Lane Intro / Celebration references.
- `onboarding-tutorial`: Remove the Lane Intro phase, "Non-spotlighted Nav Tabs Visually Disabled" requirement, and Celebration-after-Lane-Intro step; update the completion trigger.
- `onboarding-celebration`: Revive as a two-tier overlay (guest light / post-signup confetti), gated on home-selector completion and shown once per session, decoupled from the removed Lane Intro.
- `post-signup-dialog`: Open after the post-signup celebration is dismissed (sequence: celebrate → setup).

### Removed Capabilities / Dead-Spec Cleanup
<!-- These are not requirement-format deltas: dashboard-lane-introduction is already a tombstone, and state-transition-diagram is a documentation-style spec. Both are cleaned up directly. -->
- `dashboard-lane-introduction`: Delete the dead spec file (all its requirements are already tombstoned `(REMOVED)`); the Lane Intro sequence no longer exists in code.
- `state-transition-diagram`: Correct the diagram doc (remove the `detail` state and "Generate Dashboard CTA" transition; completion on My Artists arrival). Documentation-style spec, corrected in place.

## Impact

- **Frontend code**:
  - `src/hooks/auth-hook.ts` — feedback on block, Settings/Welcome exceptions, free-roam after dashboard.
  - `src/routes/settings/settings-route.{ts,html}` — guest-adaptive ACCOUNT section, guest language/home handling.
  - `src/routes/dashboard/dashboard-route.{ts,html}` — `maybeCelebrate()` gating, celebration → PostSignupDialog sequence.
  - `src/routes/my-artists/my-artists-route.ts` — completion on `.attached()`; remove hype-change completion block.
  - `src/components/celebration-overlay/*` — add `confetti` bindable (revive component).
  - `src/services/nav-dimming-service.ts` — delete; remove its single caller in `dashboard-route.ts`.
  - i18n: snackbar copy for blocked-nav feedback; guest auth-entry / celebration strings.
- **No backend / proto / infra changes.** Language change for guests is local-only (cannot persist via `UserService.UpdatePreferredLanguage`).
- **Tests**: Vitest for the route-guard decision table (new feedback paths, Settings/Welcome exceptions, free roam), my-artists completion-on-arrival, celebration tier gating; Playwright onboarding flow updates.
- **Dependency**: builds on the merged `refine-onboarding-copy` (coach mark is already tap-to-dismiss; `onboarding-tutorial` is at its latest version).
