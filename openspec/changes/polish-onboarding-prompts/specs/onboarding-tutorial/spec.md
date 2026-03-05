## MODIFIED Requirements

### Requirement: Step 5 Passion Level Explanation Timing

The Step 5 passion explanation SHALL provide immediate visual feedback on tap and appear after a shorter delay, replacing the current 3-second silent wait.

#### Scenario: Step 5 - Passion Level changed (MODIFIED)

- **WHEN** a user is at Step 5
- **AND** the user changes the Passion Level of the highlighted artist
- **THEN** the passion button SHALL immediately show a brief highlight/pulse animation (scale 1 -> 1.1 -> 1, ~300ms) as visual confirmation that the selection registered
- **AND** the system SHALL display the notification explanation after an 800ms delay (not 3000ms)
- **AND** the system SHALL advance `onboardingStep` to 6

---

### Requirement: Sign-up Modal Entrance Animation

The sign-up modal (Step 6) SHALL animate on entrance to match the visual polish of the onboarding flow.

#### Scenario: Sign-up modal entrance

- **WHEN** the sign-up modal becomes visible (Step 6 activation or page reload at Step 6)
- **THEN** the modal content panel SHALL animate in with a scale + fade effect (scale 0.95 -> 1, opacity 0 -> 1)
- **AND** the animation duration SHALL be 400ms with cubic-bezier spring easing
- **AND** a subtle radial gradient glow SHALL appear behind the modal content using the brand-primary color at low opacity

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the sign-up modal entrance animation SHALL be skipped
- **AND** the modal SHALL appear instantly without the radial glow animation
