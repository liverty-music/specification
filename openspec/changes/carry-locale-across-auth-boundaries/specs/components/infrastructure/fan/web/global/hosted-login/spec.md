## ADDED Requirements

### Requirement: Login Screen Follows the Language the App Requests

The hosted login screen SHALL choose its language with one rule: the language the app asked for when it redirected to the hosted login, else the browser's preferred language when the hosted login supports it, else English. A language remembered by the hosted login from an earlier visit (including one picked with the in-login language selector) SHALL NOT win over the language the app asks for. A language the app asks for that the hosted login does not allow SHALL be ignored, and the rest of the rule applies. The rule is the same for every app that sends users to the shared hosted login (fan app, organizer console, admin app).

#### Scenario: App language wins over the browser language

- **WHEN** the app asks for Japanese
- **AND** the browser's preferred language is English
- **THEN** the hosted login screen is in Japanese

#### Scenario: App language wins over a language remembered from an earlier visit

- **WHEN** a user picked English with the in-login language selector on an earlier visit
- **AND** the app now asks for Japanese
- **THEN** the hosted login screen is in Japanese

#### Scenario: No language requested

- **WHEN** the app redirects to the hosted login without asking for a language
- **AND** the browser's preferred language is Japanese
- **THEN** the hosted login screen is in Japanese

#### Scenario: Unsupported browser language and no request

- **WHEN** the app redirects to the hosted login without asking for a language
- **AND** the browser's preferred language is one the hosted login does not offer
- **THEN** the hosted login screen is in English

#### Scenario: App in English on a browser in another supported language

- **WHEN** the fan app, showing English on a browser whose preferred language is German, sends the user to the hosted login
- **THEN** the hosted login screen is in English, matching the app
