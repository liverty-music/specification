## MODIFIED Requirements

### Requirement: Complete button is tappable on all devices
The complete button ("ダッシュボードを生成する") SHALL be tappable on both desktop and mobile devices. The canvas element SHALL NOT intercept pointer events in the button's area.

#### Scenario: Mobile tap on complete button
- **WHEN** user taps the complete button on a mobile device
- **THEN** the `onViewSchedule()` handler SHALL fire
- **AND** the user SHALL be navigated to the loading sequence

#### Scenario: Desktop click on complete button
- **WHEN** user clicks the complete button on desktop
- **THEN** the `onViewSchedule()` handler SHALL fire
