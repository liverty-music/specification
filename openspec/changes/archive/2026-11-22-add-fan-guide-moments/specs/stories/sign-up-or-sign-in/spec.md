# Delta for stories/sign-up-or-sign-in

## MODIFIED Requirements

### Requirement: Sign-up and sign-in start only where the person chooses

The system SHALL provide Passkey authentication through hosted login. Sign-up and sign-in SHALL start only from a control the person chooses, and never from a forced step or a modal that cannot be closed: sign-up from the Sign Up banners on the Timetable and My Artists, a Concert page, the 「Sign Up」 of the dialog that a guest's press on the ticket sale notification button in the concert sheet opens, the hype snack's 「Sign Up」, the 「Sign Up」 of the out-of-range notice in a guest's concert sheet, and Settings; sign-in from the Log In link on the landing page, Settings and the account status control. After hosted login returns to `/auth/callback`, the app SHALL resolve the account as "A sign-in from any screen resolves the account with Create" states and SHALL then open the screen the person started from when that screen asked to be returned to, and the Timetable otherwise.

#### Scenario: Initiate Login from Landing Page

- **WHEN** a person clicks the Log In link on the landing page
- **THEN** the system SHALL redirect the person to hosted login
- **AND** the request SHALL include the correct Client ID and PKCE challenge

#### Scenario: Sign-up from the Timetable banner

- **WHEN** a guest presses Sign Up on the Timetable's signup banner and completes sign-up
- **THEN** the account is resolved and the Timetable opens

#### Scenario: Sign-up from a concert page returns to it

- **WHEN** a guest starts sign-up from a Concert page and completes it
- **THEN** the account is resolved and the same Concert page opens

#### Scenario: No forced sign-up

- **WHEN** a guest follows artists, chooses a home area and opens the Timetable
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

#### Scenario: Sign-up from the ticket sale notification button

- **WHEN** a guest presses the ticket sale notification button in a concert sheet
- **THEN** a dialog says an account is needed, and no sign-up starts until the guest presses its 「Sign Up」
- **WHEN** the guest presses 「あとで」
- **THEN** the dialog closes and the concert sheet stays open

