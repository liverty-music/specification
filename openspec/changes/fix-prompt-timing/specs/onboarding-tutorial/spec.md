# Onboarding Tutorial -- Delta (fix-prompt-timing)

## ADDED Requirements

### Requirement: No Permission Prompts During Onboarding Steps 1-6

The system SHALL suppress all permission prompts (PWA install banner, push notification opt-in) while the user is progressing through onboarding Steps 1-6. Permission prompts are deferred until after Step 7 (COMPLETED).

#### Scenario: PWA install suppressed during tutorial

- **WHEN** the user is at any onboarding step between 1 and 6
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL capture the event for later use
- **BUT** the system SHALL NOT display the PWA install banner

#### Scenario: Notification prompt suppressed during tutorial

- **WHEN** the user is at any onboarding step between 1 and 6
- **THEN** the system SHALL NOT render or evaluate the notification prompt component

#### Scenario: Prompts become eligible after completion

- **WHEN** the user completes Step 6 and transitions to Step 7 (COMPLETED)
- **THEN** permission prompts SHALL become eligible according to the prompt-timing capability rules
- **AND** the onboarding tutorial SHALL NOT block prompt display after this point
