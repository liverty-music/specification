## ADDED Requirements

### Requirement: Celebration Overlay on Dashboard Generation

The system SHALL display a full-screen celebration overlay when the user first arrives at the Dashboard during onboarding, providing an emotional payoff after completing artist discovery.

#### Scenario: Celebration overlay appears on first dashboard visit

- **WHEN** the user navigates to the Dashboard during onboarding (Step 3)
- **AND** `onboarding.currentStep` transitions to `DASHBOARD`
- **THEN** the system SHALL display a full-screen celebration overlay
- **AND** the overlay SHALL display the text "あなただけのタイムテーブルが完成しました！" centered on screen
- **AND** the overlay SHALL play a confetti/particle CSS animation in the background
- **AND** the overlay SHALL remain visible for 2.5 seconds
- **AND** the overlay SHALL then fade out over 400ms

#### Scenario: Dashboard content hidden during celebration

- **WHEN** the celebration overlay is visible
- **THEN** the dashboard content (lanes, cards, headers) SHALL NOT be visible beneath the overlay
- **AND** the user SHALL NOT be able to interact with dashboard content

#### Scenario: Celebration does not replay

- **WHEN** the user has already seen the celebration overlay during this onboarding session
- **AND** the user returns to the Dashboard (e.g., via route guard redirect)
- **THEN** the system SHALL NOT display the celebration overlay again

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the confetti/particle animation SHALL be skipped
- **AND** the celebration text SHALL appear instantly and remain for 1.5 seconds
- **AND** the overlay SHALL disappear instantly (no fade)

#### Scenario: Celebration transitions to lane introduction

- **WHEN** the celebration overlay fade-out completes
- **THEN** the system SHALL proceed to the region selection flow (if needed) or the lane introduction sequence
