<!-- spec: post-signup-dialog | target: components/infrastructure/fan/web/global/post-signup-dialog | flags: CLASSNAME | new_name: Dialog footer button reflects completion state -->

### Requirement: Dialog footer button reflects completion state

The footer button label in the post-signup dialog SHALL dynamically reflect whether the user has completed all available actions.

#### Scenario: Button switches to "Close" after enabling notifications

- **WHEN** the user taps the notification opt-in button
- **AND** enabling push notifications succeeds
- **AND** installing the app as a PWA is not offered (no separate install action is pending)
- **THEN** the notification permission SHALL become granted
- **AND** all available actions SHALL be considered complete
- **AND** the footer button SHALL display "Close"
