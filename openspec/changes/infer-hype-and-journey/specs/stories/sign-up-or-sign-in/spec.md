## MODIFIED Requirements

### Requirement: Every sign-in resolves the account with Create

After a sign-in, whether at the end of the tutorial, through the Login link or from any other screen, when the app remembers no account for the signed-in identity, it SHALL call UserUseCase.Create with the app's current display language as preferred language and, when the guest chose a home, that home, and SHALL remember the returned account for that identity. Create is the one call that both registers a new identity and returns an existing one, so a returning fan is treated the same as a new one. When Create reports that the identity has no account and no home was given, the app SHALL ask for the home area in a sheet the person cannot close, call Create again with the chosen home, and then continue to where the sign-up started. Signing out SHALL forget the remembered account, so the next sign-in resolves it with Create again. After the account is resolved, the guest's follows and hype levels are merged as the story stories/merge-guest-data-on-signup describes.

#### Scenario: New fan finishes the tutorial

- **WHEN** a guest who chose home JP-13 during onboarding and uses the app in Japanese signs up at the end of the tutorial
- **THEN** a new account is created with home JP-13 and preferred language `ja`, and the app uses it from then on

#### Scenario: Sign-up from the event page without a home

- **WHEN** a guest who never chose a home signs up from an event page
- **THEN** the app asks for the home area in a sheet that cannot be closed, creates the account with the chosen home, and returns to the event page

#### Scenario: Returning fan signs in on a new device

- **WHEN** a fan with an account whose language is `en` signs in through the Login link on a device set to Japanese
- **THEN** the app uses the existing account, does not ask for a home area, and its preferred language stays `en`

#### Scenario: Sign out and back in

- **WHEN** a fan signs out and signs in again with the same identity
- **THEN** the app resolves the same account again and shows the fan's own follows
