## ADDED Requirements

### Requirement: Every start of sign-up or sign-in is reported

Each time the fan app sends a person to hosted login to sign up or to sign in, from any screen or control, it SHALL send one usage analytics event just before leaving, stating whether sign-up or sign-in was started and the screen or control it was started from. When the analytics library has not loaded by then, the event SHALL be kept on the device and sent when the person comes back to the fan app, with the time it was started. The event SHALL obey the analytics opt-out. Signing in again to manage passkeys, by a person already signed in, is not a start of sign-in.

#### Scenario: Sign-up from a banner
- **WHEN** a guest taps the sign-up prompt on the Dashboard
- **THEN** one event is sent stating sign-up and the Dashboard prompt, before the app leaves for hosted login

#### Scenario: Sign-in from the landing page
- **WHEN** a visitor taps `[Log In]` on the landing page
- **THEN** one event is sent stating sign-in and the landing page

#### Scenario: Started before analytics loaded
- **WHEN** a visitor taps `[Log In]` before the analytics library has loaded, and comes back signed in
- **THEN** one sign-in event is sent on the return, with the time of the tap

#### Scenario: Analytics off
- **WHEN** a person with analytics off starts sign-up from Settings
- **THEN** no event is sent and the app leaves for hosted login as usual
