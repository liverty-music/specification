## ADDED Requirements

### Requirement: Sequential Lane Header Spotlight

The system SHALL introduce each dashboard lane by sequentially spotlighting the STAGE headers with explanatory coach marks before spotlighting the first concert card.

#### Scenario: Lane introduction begins after region selection

- **WHEN** the celebration overlay has faded
- **AND** the region selection (if needed) has completed
- **THEN** the system SHALL begin the lane introduction sequence
- **AND** scrolling SHALL be disabled during the entire sequence

#### Scenario: HOME STAGE header spotlight

- **WHEN** the lane introduction sequence begins
- **THEN** the system SHALL spotlight the HOME STAGE header element
- **AND** the coach mark SHALL display: "地元のライブ情報！"
- **AND** the spotlight SHALL remain for 2 seconds or until the user taps

#### Scenario: NEAR STAGE header spotlight

- **WHEN** the HOME STAGE spotlight completes (2s timeout or user tap)
- **THEN** the system SHALL spotlight the NEAR STAGE header element
- **AND** the coach mark SHALL display: "近くのエリアのライブも！"
- **AND** the spotlight SHALL remain for 2 seconds or until the user taps

#### Scenario: AWAY STAGE header spotlight

- **WHEN** the NEAR STAGE spotlight completes (2s timeout or user tap)
- **THEN** the system SHALL spotlight the AWAY STAGE header element
- **AND** the coach mark SHALL display: "全国のライブ情報もチェック！"
- **AND** the spotlight SHALL remain for 2 seconds or until the user taps

#### Scenario: Transition to first card spotlight

- **WHEN** the AWAY STAGE spotlight completes
- **THEN** the system SHALL proceed to the existing Step 3 card spotlight behavior
- **AND** scrolling SHALL remain disabled until the card is tapped

### Requirement: Lane Introduction State Management

The lane introduction sequence SHALL be managed locally within the dashboard component, not persisted in the onboarding service.

#### Scenario: Lane intro state is ephemeral

- **WHEN** the dashboard component manages the lane introduction
- **THEN** the intro state SHALL be a local variable (e.g., `laneIntroPhase: 'home' | 'near' | 'away' | 'card' | 'done'`)
- **AND** the state SHALL NOT be written to `liverty:onboardingStep` in LocalStorage

#### Scenario: Page reload during lane introduction

- **WHEN** the user reloads the page during the lane introduction sequence
- **THEN** the system SHALL restart the lane introduction from the beginning (HOME STAGE)
- **AND** the celebration overlay SHALL NOT replay (it uses a separate one-time flag)
