## MODIFIED Requirements

### Requirement: Celebration Overlay on Dashboard — Repositioned After Lane Intro

The system SHALL display the Celebration Overlay after the Lane Intro sequence completes, not before. Opening the Celebration Overlay SHALL advance `onboardingStep` from `'dashboard'` to `'my-artists'`. The overlay is dismissed by a tap anywhere on the screen.

#### Scenario: Celebration overlay appears after Lane Intro

- **WHEN** the Lane Intro AWAY phase tap is received
- **THEN** the system SHALL open the Celebration Overlay
- **AND** opening the overlay SHALL advance `onboardingStep` to `'my-artists'`
- **AND** the overlay SHALL display "あなただけのタイムテーブルが完成しました！"
- **AND** the overlay SHALL display a secondary message: "自由にタイムテーブルを触ってみよう"
- **AND** the overlay SHALL play confetti/particle animation

#### Scenario: Celebration dismissed by tap

- **WHEN** the user taps anywhere on the Celebration Overlay
- **THEN** the overlay SHALL fade out over 400ms
- **AND** blocker divs SHALL be deactivated
- **AND** scroll lock SHALL be released
- **AND** the user SHALL enter free exploration mode on the Dashboard

#### Scenario: Celebration does not replay

- **WHEN** the user has already seen the Celebration Overlay during this onboarding session
- **AND** the user returns to the Dashboard
- **THEN** the system SHALL NOT display the Celebration Overlay again

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the confetti/particle animation SHALL be skipped
- **AND** the overlay SHALL appear instantly and remain until tapped
- **AND** the overlay SHALL disappear instantly (no fade) on tap

## REMOVED Requirements

### Requirement: Celebration appears before Lane Intro

**Reason**: Celebration before Lane Intro means users are congratulated before seeing what they've built. Moving it after Lane Intro makes it the natural emotional payoff and explicit end of the guided sequence.

**Migration**: In `dashboard-route.ts`, remove the `showCelebration → onCelebrationComplete → startLaneIntro` sequence. Replace with `startLaneIntro → (AWAY phase complete) → showCelebration`.

### Requirement: Celebration auto-dismisses after 2.5 seconds

**Reason**: Auto-dismiss removes user agency at the moment of highest engagement. Tap-to-dismiss lets users read the secondary message ("自由にタイムテーブルを触ってみよう") before proceeding.

**Migration**: Remove the `displayDuration` setTimeout in `celebration-overlay.ts`. Fire the completion callback only when the user taps (click/pointerdown event on the overlay).

### Requirement: Celebration transitions to region selection flow

**Reason**: Region selection now happens inline during the Lane Intro HOME phase, before Celebration.

**Migration**: Remove the region-selection trigger from `onCelebrationComplete`. Region selection is handled within `startLaneIntroHomePhase()`.
