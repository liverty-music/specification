## ADDED Requirements

### Requirement: Sign-in opens in the console's language

Every redirect from the console to the hosted login screen (the sign-in started when an operator opens the console without a session, and the sign-in started after an involuntary logout) SHALL ask the hosted login to show the language the console is showing at that moment.

#### Scenario: Operator who chose Japanese on an English browser

- **WHEN** an operator who switched the console to Japanese on a browser whose preferred language is English opens the console without a session
- **THEN** the hosted login screen opens in Japanese

#### Scenario: Operator who chose English on a Japanese browser

- **WHEN** an operator who switched the console to English on a browser whose preferred language is Japanese is logged out because the session can no longer be renewed
- **THEN** the hosted login screen opens in English

## MODIFIED Requirements

### Requirement: Japanese or English, chosen on the device

Every label, message and error the console shows SHALL come in Japanese and in English. On first open the console SHALL use the language saved on this device; when none is saved it SHALL use Japanese when the browser's preferred language is Japanese and English otherwise. An operator SHALL be able to switch the language from the account menu; the switch SHALL change every text on the page at once without a reload and SHALL be saved on this device only. The page's declared language SHALL always match the language shown, so that screen readers and the browser's text handling follow it.

#### Scenario: First open on a Japanese browser

- **WHEN** an operator opens the console for the first time in a browser whose preferred language is Japanese
- **THEN** the console is in Japanese and the page declares Japanese

#### Scenario: Browser in another language

- **WHEN** an operator opens the console for the first time in a browser whose preferred language is French
- **THEN** the console is in English and the page declares English

#### Scenario: Operator switches to English

- **WHEN** an operator switches the language to English from the account menu
- **THEN** every text on the page changes to English without a reload, the page declares English, and the next visit on this device opens in English

#### Scenario: Every text follows a switch

- **WHEN** an operator on Settings switches from English to Japanese, and then opens the concert editor
- **THEN** the business detail labels, the account menu's mark on the chosen language, the concert type choices and every option list are in Japanese
