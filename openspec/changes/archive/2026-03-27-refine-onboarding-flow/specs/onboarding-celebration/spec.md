## MODIFIED Requirements

### Requirement: Celebration Overlay on Dashboard — Repositioned After Lane Intro

The system SHALL display the Celebration Overlay after the Lane Intro sequence completes, not before. Opening the Celebration Overlay SHALL advance `onboardingStep` from `'dashboard'` to `'my-artists'`. The overlay is dismissed by a tap anywhere on the screen. The celebration text SHALL be visually prominent with bold typography, large font size, and glowing text effects to create a sense of accomplishment.

#### Scenario: Celebration overlay appears after Lane Intro

- **WHEN** the Lane Intro AWAY phase tap is received
- **THEN** the system SHALL open the Celebration Overlay
- **AND** opening the overlay SHALL advance `onboardingStep` to `'my-artists'`
- **AND** the overlay SHALL display "あなただけのタイムテーブルが完成しました！"
- **AND** the overlay SHALL display a secondary message: "自由にタイムテーブルを触ってみよう"
- **AND** the overlay SHALL play confetti/particle animation

#### Scenario: Celebration text is visually prominent

- **WHEN** the Celebration Overlay is displayed
- **THEN** the primary message SHALL use a large display font size (at least `--step-4`)
- **AND** the primary message SHALL use bold font weight
- **AND** the primary message SHALL have a glowing text-shadow effect
- **AND** the secondary message SHALL be visually distinct from the primary (smaller size, lighter weight)
- **AND** the text entry animation SHALL scale up from small to full size

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
