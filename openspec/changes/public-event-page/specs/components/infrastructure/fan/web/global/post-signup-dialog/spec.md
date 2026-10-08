# Spec Delta

## ADDED Requirements

### Requirement: Sign-up from an event page skips the celebration and the dialog

A sign-up that the fan started on an Event page SHALL NOT show the celebration overlay or the post-signup dialog, neither on the Event page the fan returns to nor later on the Dashboard. A sign-up started anywhere else SHALL keep showing them as the other requirements of this surface state.

#### Scenario: Guest signs up while buying

- **WHEN** a guest starts sign-up on an Event page, completes it and later opens the Dashboard
- **THEN** neither the celebration overlay nor the post-signup dialog is shown

#### Scenario: Sign-up from the landing page

- **WHEN** a guest starts sign-up from the Welcome page and completes it
- **THEN** the celebration overlay and then the post-signup dialog are shown on the Dashboard
