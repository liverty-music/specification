# Onboarding Celebration

## Purpose

Provides an emotional payoff on the Dashboard, gated on the timetable being real (region set, data loaded). Fired from a single `maybeCelebrate()` decision point in two tiers: a light (no-confetti) acknowledgement on a guest's first dashboard arrival during onboarding, and a full confetti celebration on the post-signup redirect that hands off to the PostSignupDialog.

## Requirements

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

### Requirement: Celebration Reveals the Timetable Behind the Text

The celebration overlay SHALL keep the completed dashboard timetable visible behind the celebration text rather than fully obscuring it, so the overlay reveals the payoff it is announcing. The overlay backdrop SHALL NOT apply a full-viewport opaque veil or a full-viewport blur of the content behind it. Darkening SHALL be localized to the region behind the heading and sub-text (a feathered "text-lens"), leaving the screen edges showing the timetable's colors. Regardless of the colors behind it — including the brightest stage cards — the heading and sub-text SHALL remain legible. This requirement governs only the overlay's backdrop and text-contrast treatment; it does not change the celebration tiers, gating, once-per-tier behavior, confetti flag, tap-to-dismiss, or reduced-motion handling defined by `Requirement: Two-Tier Celebration Overlay`.

#### Scenario: Timetable colors remain visible at the screen edges

- **WHEN** the celebration overlay is displayed over the loaded timetable
- **THEN** the timetable's card colors SHALL remain visible at the screen edges (outside the text region)
- **AND** the overlay SHALL NOT cover the viewport with an opaque veil or a full-viewport blur

#### Scenario: Heading and sub-text stay legible over bright cards

- **WHEN** the celebration overlay is displayed over bright/light-colored timetable cards (e.g. near-stage cyan)
- **THEN** both the heading and the sub-text SHALL remain legible against that background

#### Scenario: Existing celebration behavior is preserved

- **WHEN** the celebration overlay is shown in either tier (guest light or post-signup full)
- **THEN** the tier gating, at-most-once-per-tier persistence, confetti flag, tap-to-dismiss, and `prefers-reduced-motion` handling SHALL behave exactly as before this change
