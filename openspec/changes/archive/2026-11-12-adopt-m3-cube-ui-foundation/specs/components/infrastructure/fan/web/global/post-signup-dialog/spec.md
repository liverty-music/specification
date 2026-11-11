## MODIFIED Requirements

### Requirement: Dialog title and aria-label use i18n bindings
All user-visible strings in the post-signup dialog SHALL come from the translation resources of the active locale. No display string is fixed in the markup.

#### Scenario: Title renders in Japanese locale
- **WHEN** the notification step is displayed
- **AND** the active locale is `ja`
- **THEN** the title SHALL read 「新着ライブをいち早くお知らせ」

#### Scenario: Title renders in active locale
- **WHEN** the notification step is displayed
- **AND** the active locale is `en`
- **THEN** the title SHALL be the English equivalent of the Japanese title

#### Scenario: aria-label follows active locale
- **WHEN** the post-signup dialog is displayed
- **AND** the active locale is `en`
- **THEN** the dialog's accessible name SHALL be the English text of the current step's heading

#### Scenario: Translation key parity
- **WHEN** a string of the post-signup dialog exists in the Japanese translation resource
- **THEN** the same string SHALL exist in the English translation resource
