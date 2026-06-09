## MODIFIED Requirements

### Requirement: Global Auth Hook

The system SHALL provide a global authentication lifecycle hook (`AuthHook`) that gates SPA route loads based on authentication state only. The hook SHALL NOT enforce onboarding step ordering — there is no step machine and no ordinal `tutorialStep` comparison. For guests (unauthenticated users) the hook SHALL permit free roam across application routes (soft gate); account-only features SHALL be hidden at point of use per `guest-mode-access` rather than blocked by navigation. The dashboard SHALL be reachable at any onboarding state; a guest with no follows SHALL be guided by an in-page empty-state call-to-action toward discovery, not by a guard redirect.

#### Scenario: Authenticated user navigates to any route

- **WHEN** a user has `isAuthenticated = true`
- **THEN** the system SHALL allow the route component to load
- **AND** no onboarding-based restrictions SHALL be applied

#### Scenario: Public route is always allowed

- **WHEN** a route has `data.auth === false` (e.g. Welcome, About, auth callback, legal pages)
- **THEN** the system SHALL allow the route to load regardless of authentication or onboarding state

#### Scenario: Guest navigates to an application route

- **WHEN** a user has `isAuthenticated = false`
- **AND** the target route is an application route (e.g. dashboard, discovery, my-artists, tickets, settings)
- **THEN** the system SHALL allow the route to load (guest free roam / soft gate)
- **AND** the system SHALL NOT redirect based on any onboarding step
- **AND** account-only features on the destination SHALL be hidden at point of use per `guest-mode-access`

#### Scenario: Guest with no follows lands on the dashboard

- **WHEN** a user has `isAuthenticated = false`
- **AND** the user navigates to `/dashboard` with zero followed artists
- **THEN** the system SHALL allow the dashboard to load
- **AND** the dashboard SHALL present an empty-state call-to-action pointing to discovery
- **AND** the system SHALL NOT redirect the user away from the dashboard

### Requirement: Settings Reachable During Onboarding

The system SHALL allow an unauthenticated user to navigate to the Settings route at any onboarding state, so that the sign-in / sign-up and language affordances are always reachable.

#### Scenario: Guest opens Settings during onboarding

- **WHEN** a user has `isAuthenticated = false`
- **AND** `OnboardingService.isOnboarding` is `true`
- **AND** the user navigates to `/settings`
- **THEN** the system SHALL allow the Settings route to load
- **AND** the system SHALL NOT redirect away from Settings

### Requirement: Welcome Reachable During Onboarding

The system SHALL allow an unauthenticated user in onboarding to navigate back to the Welcome (landing) route to re-read the value proposition, without being bounced forward.

#### Scenario: Onboarding guest returns to Welcome

- **WHEN** a user has `isAuthenticated = false`
- **AND** `OnboardingService.isOnboarding` is `true`
- **AND** the user navigates to `/` (Welcome)
- **THEN** the system SHALL allow the Welcome route to load
- **AND** merely viewing Welcome SHALL NOT change onboarding state
- **AND** onboarding state SHALL change only via the completion latch (`finish()`), never by viewing Welcome

## REMOVED Requirements

### Requirement: Onboarding Dashboard Readiness

**Reason**: The `readyForDashboard` predicate existed only to gate the forced discovery→dashboard transition. With the soft gate, the dashboard is always reachable and no readiness predicate is needed; the follow/concert thresholds now drive the coach-mark hint only (computed from live counts in `DiscoveryRoute`).

**Migration**: Delete `OnboardingService.readyForDashboard`, `setDiscoveryCounts`, and the mirrored `followedCount` / `artistsWithConcertsCount` fields. Move `DASHBOARD_FOLLOW_TARGET` / `DASHBOARD_CONCERT_TARGET` to a constants module consumed directly by `DiscoveryRoute` for the coach-mark trigger.
