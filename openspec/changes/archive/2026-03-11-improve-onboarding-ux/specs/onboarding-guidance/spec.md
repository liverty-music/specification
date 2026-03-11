## MODIFIED Requirements

### Requirement: CTA button visibility during onboarding

- **REMOVED**: The "ダッシュボードを生成する" CTA button is removed from the discover page. The CTA is replaced by a coach mark spotlight on the nav-bar Dashboard icon (defined in `onboarding-tutorial` Step 1 completion).

**Reason**: The nav-bar Dashboard icon spotlight teaches users about navigation while serving as the CTA. A separate button is redundant.
**Migration**: Remove the `complete-button-wrapper` and `complete-button` elements from `discover-page.html`. CTA behavior is handled by the coach mark component targeting `[data-nav-dashboard]`.

### Requirement: Staged progress messages

The system SHALL display contextual progress messages that change as the user follows more artists.

#### Scenario: After following 1 artist

- **WHEN** followedCount becomes 1
- **THEN** the guidance area SHALL display "いいね！あと2組！"

#### Scenario: After following 2 artists

- **WHEN** followedCount becomes 2
- **THEN** the guidance area SHALL display "あと1組！"

#### Scenario: After following 3 or more artists

- **WHEN** followedCount reaches 3 (TUTORIAL_FOLLOW_TARGET)
- **THEN** the guidance area SHALL display "準備完了！"
- **AND** the system SHALL NOT display a separate CTA button
- **AND** the progress bar SHALL switch to showing concert search completion status

## ADDED Requirements

### Requirement: Concert Search Progress Bar

The system SHALL display a progress bar on the discover page that tracks concert search completion for followed artists, replacing the numeric counter after 3 artists are followed.

#### Scenario: Progress bar appears after 3 follows

- **WHEN** `followedCount >= 3` during onboarding
- **THEN** the progress bar SHALL display below the guidance message
- **AND** the progress bar fill width SHALL represent `completedSearchCount / followedCount * 100%`
- **AND** the progress bar SHALL use a continuous fill animation (not discrete steps)

#### Scenario: Concert search completes for an artist

- **WHEN** a `SearchNewConcerts` call completes (success or timeout) for a followed artist
- **THEN** the progress bar fill SHALL update to reflect the new completion ratio
- **AND** the update SHALL animate smoothly (300ms transition)

#### Scenario: All searches complete

- **WHEN** all followed artists (minimum 3) have completed concert searches
- **THEN** the system SHALL activate the nav-bar Dashboard icon coach mark (per `onboarding-tutorial` Step 1 completion)

#### Scenario: Search timeout

- **WHEN** a concert search for an artist exceeds 15 seconds
- **THEN** the system SHALL treat the search as completed for progress bar purposes
- **AND** the system SHALL NOT block CTA activation due to the timeout
