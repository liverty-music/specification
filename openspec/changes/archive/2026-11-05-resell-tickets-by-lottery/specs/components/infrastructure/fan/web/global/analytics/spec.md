# Spec Delta

## MODIFIED Requirements

### Requirement: Session recordings hide what the fan types and reads

When both Analytics and Session replay are on in Settings, the fan app SHALL record the session for replay with every text on screen and every input value masked, including password and hidden fields, and SHALL NOT record the checkout, lottery entry, resale entry, identity check and Settings screens at all. With either toggle off, nothing SHALL be recorded. A recording SHALL be linked to the same person as the fan's analytics events.

#### Scenario: Masked text
- **WHEN** a recorded fan opens the Dashboard, where artist names and the fan's home area are shown
- **THEN** the recording shows the layout and the fan's taps, and every text in it is masked

#### Scenario: Screen that is never recorded
- **WHEN** a recorded fan opens the checkout
- **THEN** no recording is made while the checkout is shown, and recording resumes on the next screen that is recorded

#### Scenario: Session replay off
- **WHEN** the fan turns Session replay off and keeps Analytics on
- **THEN** recording stops and events are still sent
