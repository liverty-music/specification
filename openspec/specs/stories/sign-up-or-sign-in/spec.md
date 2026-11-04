# Sign up or sign in

## Purpose

Defines user authentication behavior: sign up / sign in, session restoration on cold start, and the server-side session monitoring policy.

```mermaid
usecase-beta
direction LR
actor Fan("fan")
systemBoundary "Liverty Music"
  Goal("Sign up or sign in")
  UserUseCaseCreate("UserUseCase.Create")
end
Fan --> Goal
Goal ..> : include UserUseCaseCreate
```

## Requirements

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

### Requirement: Sign-up and sign-in start only where the person chooses

The system SHALL provide Passkey authentication through hosted login. Sign-up and sign-in SHALL start only from a control the person chooses, and never from a forced step or a modal that cannot be closed: sign-up from the Sign Up banners on the Dashboard and My Artists, the All Nearby view's prompt, an Event page, the ticket sale notification button of a guest's event detail sheet, the hype snack's 「登録する」, the 「登録する」 of the out-of-range notice in a guest's event detail sheet, and Settings; sign-in from the Log In link on the landing page, Settings and the account status control. After hosted login returns to `/auth/callback`, the app SHALL resolve the account as "A sign-in from any screen resolves the account with Create" states and SHALL then open the screen the person started from when that screen asked to be returned to, and the Dashboard otherwise.

#### Scenario: Initiate Login from Landing Page

- **WHEN** a person clicks the Log In link on the landing page
- **THEN** the system SHALL redirect the person to hosted login
- **AND** the request SHALL include the correct Client ID and PKCE challenge

#### Scenario: Sign-up from the Dashboard banner

- **WHEN** a guest presses Sign Up on the Dashboard's signup banner and completes sign-up
- **THEN** the account is resolved and the Dashboard opens

#### Scenario: Sign-up from an event page returns to it

- **WHEN** a guest starts sign-up from an Event page and completes it
- **THEN** the account is resolved and the same Event page opens

#### Scenario: No forced sign-up

- **WHEN** a guest follows artists, chooses a home area and opens the Dashboard
- **THEN** no sign-up starts and no modal that cannot be closed appears

#### Scenario: Registration Callback API Failure

- **WHEN** the `Create` RPC call fails during the registration callback, including `ALREADY_EXISTS` because the email belongs to another identity
- **THEN** the system SHALL log the error
- **AND** the system SHALL still complete the authentication flow (user can use the app)
- **AND** the local user record will be created on a subsequent provisioning attempt

#### Scenario: Registration Callback for an already registered identity

- **WHEN** the signed-in identity already has an account and `Create` is called during the callback
- **THEN** `Create` returns the existing account unchanged
- **AND** the system SHALL continue exactly as for a newly created account

### Requirement: A sign-in from any screen resolves the account with Create

After a sign-in from any screen, when the app remembers no account for the signed-in identity, it SHALL call UserUseCase.Create with the app's current display language as preferred language and, when the guest chose a home, that home, and SHALL remember the returned account for that identity. Create is the one call that both registers a new identity and returns an existing one, so a returning fan is treated the same as a new one. When the guest chose no home, the account is created without one and the app continues to where the sign-up started; the home is asked for later, on the Dashboard or My Artists (components/infrastructure/fan/web/global/user-home-selector), never in the sign-up itself. Signing out SHALL forget the remembered account, so the next sign-in resolves it with Create again. After the account is resolved, the guest's follows and hype levels are merged as the story stories/merge-guest-data-on-signup describes.

#### Scenario: New fan signs up after choosing a home

- **WHEN** a guest who chose home JP-13 during onboarding and uses the app in Japanese signs up from the Dashboard banner
- **THEN** a new account is created with home JP-13 and preferred language `ja`, and the app uses it from then on

#### Scenario: Sign-up from the event page without a home

- **WHEN** a guest who never chose a home signs up from an event page
- **THEN** the account is created without a home and the event page opens again, with no home sheet
- **AND** the next time the fan opens the Dashboard or My Artists, the app asks for the home area in a sheet that cannot be closed

#### Scenario: Returning fan signs in on a new device

- **WHEN** a fan with an account whose language is `en` signs in through the Login link on a device set to Japanese
- **THEN** the app uses the existing account, does not ask for a home area, and its preferred language stays `en`

#### Scenario: Sign out and back in

- **WHEN** a fan signs out and signs in again with the same identity
- **THEN** the app resolves the same account again and shows the fan's own follows
