## MODIFIED Requirements

### Requirement: Progressive Loading Animation
The system SHALL display a multi-phase animated loading sequence with visual richness during data aggregation, replacing a simple spinner.

#### Scenario: Phase 1 display (0-2 seconds)
- **WHEN** the loading sequence begins
- **THEN** the system SHALL display the message "あなたのMusic DNAを構築中..."
- **AND** the message SHALL appear with a fade-in animation

#### Scenario: Phase 2 display (2-5 seconds)
- **WHEN** 2 seconds have elapsed since the loading sequence began
- **THEN** the system SHALL transition to display the message "全国のライブスケジュールと照合中..."
- **AND** the transition SHALL use a smooth crossfade animation

#### Scenario: Phase 3 display (5+ seconds)
- **WHEN** 5 seconds have elapsed since the loading sequence began
- **THEN** the system SHALL transition to display the message "AIが最新のツアー情報を検索中... 🤖"

#### Scenario: Visual progress indicator
- **WHEN** the loading sequence is active
- **THEN** the system SHALL display a visual progress indicator (e.g., progress bar, step dots, or animated ring)
- **AND** the indicator SHALL advance through the phases to communicate progress
- **AND** the indicator SHALL be styled using the design system's brand accent color

#### Scenario: Step indicator display
- **WHEN** the loading sequence transitions between phases
- **THEN** the system SHALL display a step indicator showing the current phase number (e.g., "1/3", "2/3", "3/3") or equivalent visual dots
- **AND** completed phases SHALL be visually distinguished from pending phases

#### Scenario: Visual effects beyond text
- **WHEN** the loading sequence is displayed
- **THEN** the system SHALL include at least one animated visual element beyond text (e.g., pulsing orb, particle animation, or animated gradient)
- **AND** the visual element SHALL enhance the feeling of "something being built" to match the messages

## ADDED Requirements

### Requirement: Visual Continuity from Discovery
The loading sequence SHALL maintain visual continuity with the preceding Artist Discovery screen.

#### Scenario: Consistent visual theme
- **WHEN** the user transitions from Artist Discovery to the Loading Sequence
- **THEN** the background gradient SHALL match the Artist Discovery screen's dark gradient
- **AND** the transition SHALL not introduce a jarring visual break
