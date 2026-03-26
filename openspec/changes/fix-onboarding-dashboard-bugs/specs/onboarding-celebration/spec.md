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

#### Scenario: Celebration MUST NOT appear before lane intro

- **WHEN** the Dashboard page loads during onboarding at step DASHBOARD
- **THEN** the system SHALL NOT set `showCelebration = true` in `loading()`
- **AND** the system SHALL start the lane intro sequence first
- **AND** `showCelebration` SHALL only become `true` after `completeLaneIntro()` is called

#### Scenario: Celebration does not replay

- **WHEN** the user has already seen the Celebration Overlay during this onboarding session
- **AND** the user returns to the Dashboard
- **THEN** the system SHALL NOT display the Celebration Overlay again

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the confetti/particle animation SHALL be skipped
- **AND** the overlay SHALL appear instantly and remain until tapped
- **AND** the overlay SHALL disappear instantly (no fade) on tap
