<!-- spec: post-signup-dialog | target: components/infrastructure/fan/web/global/post-signup-dialog | flags: CLASSNAME | new_name: Dialog footer button reflects completion state -->

### Requirement: PostSignupDialog footer button reflects completion state

The footer button label in PostSignupDialog SHALL dynamically reflect whether the user has completed all available actions.

#### Scenario: Button switches to "Close" after enabling notifications

- **WHEN** the user taps the notification opt-in button
- **AND** `pushService.create()` succeeds
- **AND** `canInstallPwa` is `false`
- **THEN** `notificationManager.permission` becomes `'granted'`
- **AND** `isAllDone` becomes `true`
- **AND** the footer button SHALL display "Close"
