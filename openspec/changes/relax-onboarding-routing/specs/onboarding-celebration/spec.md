## ADDED Requirements

### Requirement: Two-Tier Celebration Overlay

The system SHALL present a celebration overlay (`celebration-overlay`) at two distinct moments, gated on the dashboard timetable being real (region set and data loaded). The overlay SHALL be fired from a single decision point (`maybeCelebrate()`) and SHALL be shown at most once per tier per onboarding session, persisted via a localStorage flag. A `confetti` flag SHALL control whether the confetti animation renders.

- **Tier Z-light** (guest's first dashboard arrival): the overlay SHALL render without confetti and acknowledge that the personal timetable has been created.
- **Tier Z-full** (post-signup redirect): the overlay SHALL render with confetti, and on dismissal SHALL open the PostSignupDialog.

#### Scenario: Celebration gated on timetable readiness

- **WHEN** the dashboard is reached during onboarding or just after sign-up
- **AND** `needsRegion` is still `true` (the home-selector is open and the timetable is blurred)
- **THEN** the system SHALL NOT show the celebration overlay
- **AND** the system SHALL evaluate `maybeCelebrate()` again after `onHomeSelected()` resolves and timetable data has loaded

#### Scenario: Guest light celebration on first dashboard

- **WHEN** an unauthenticated user reaches the dashboard for the first time
- **AND** the user is still in the onboarding flow (`isOnboarding` is true) — the celebration is the onboarding creation payoff, not a surprise for a completed guest revisiting the dashboard
- **AND** the region is set and timetable data has loaded
- **AND** the light celebration has not been shown this session (the `onboarding.celebrationShown` localStorage flag is unset)
- **THEN** the system SHALL display the celebration overlay with `confetti = false`
- **AND** the system SHALL record that the light celebration has been shown via the `onboarding.celebrationShown` flag
- **AND** the overlay SHALL be dismissible by tap

#### Scenario: No light celebration for a completed guest revisiting the dashboard

- **WHEN** an unauthenticated user whose onboarding is already completed navigates to the dashboard
- **THEN** the system SHALL NOT display the light celebration overlay

#### Scenario: Post-signup full celebration then dialog

- **WHEN** a newly signed-up user is redirected to the dashboard (`liverty:postSignup:shown` pending)
- **AND** the region is set and timetable data has loaded
- **THEN** the system SHALL display the celebration overlay with `confetti = true`
- **AND** on dismissal the system SHALL open the PostSignupDialog (per `post-signup-dialog`)

#### Scenario: Celebration does not replay

- **WHEN** a user who has already seen a given celebration tier this session returns to the dashboard
- **THEN** the system SHALL NOT display that celebration tier again

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the confetti animation SHALL be skipped
- **AND** the overlay SHALL appear and disappear without transition animation

## REMOVED Requirements

### Requirement: Celebration Overlay on Dashboard — Repositioned After Lane Intro

**Reason**: The Lane Intro sequence that this requirement depended on has been removed from the implementation. The celebration is being re-grounded on dashboard-timetable readiness and split into two tiers (guest light / post-signup confetti), defined by the new "Two-Tier Celebration Overlay" requirement.

**Migration**: Remove the "after Lane Intro AWAY phase" trigger. Fire the overlay from `maybeCelebrate()` after the home-selector resolves and timetable data loads. Opening the overlay no longer advances `onboardingStep` (dashboard arrival already advances to `'my-artists'`).
