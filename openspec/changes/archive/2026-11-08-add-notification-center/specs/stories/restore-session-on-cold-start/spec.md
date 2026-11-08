## ADDED Requirements

### Requirement: The remembered account and its language are restored on launch

On every launch with a signed-in session, the app SHALL restore the fan's account from the account remembered for the signed-in identity (UserUseCase.Get) before it makes any other per-fan request. The account's preferred language SHALL be in use from then on: the language the app kept on the device before sign-in is dropped, and the account's language wins.

#### Scenario: Reopen with a remembered account

- **WHEN** a signed-in fan reopens the app
- **THEN** the fan's follows, home and language are those of their account

#### Scenario: Account language kept on a device in another language

- **WHEN** a signed-in fan opens the app in Japanese and the account's preferred language is `en`
- **THEN** the account's preferred language stays `en` and the app does not change it

#### Scenario: Language chosen on another device

- **WHEN** a fan's account language is `en` and the device kept `ja` from before sign-in
- **THEN** after the next launch the app is shown in English

## REMOVED Requirements

### Requirement: The remembered account is restored on launch
**Reason**: Replaced by "The remembered account and its language are restored on launch", which states the behavior without the scenarios of the removed behavior.
**Migration**: None.
