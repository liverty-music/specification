## ADDED Requirements

### Requirement: Every start of sign-up or sign-in is reported

Each time the fan app sends a person to hosted login to sign up or to sign in, from any screen or control, it SHALL send one usage analytics event just before leaving, stating whether sign-up or sign-in was started and the screen or control it was started from. The event SHALL obey the analytics opt-out.

#### Scenario: Sign-up from a banner
- **WHEN** a guest taps the sign-up prompt on the Dashboard
- **THEN** one event is sent stating sign-up and the Dashboard prompt, before the app leaves for hosted login

#### Scenario: Sign-in from the landing page
- **WHEN** a visitor taps `[Log In]` on the landing page
- **THEN** one event is sent stating sign-in and the landing page

#### Scenario: Analytics off
- **WHEN** a person with analytics off starts sign-up from Settings
- **THEN** no event is sent and the app leaves for hosted login as usual
