<!-- spec: post-signup-dialog | target: components/infrastructure/fan/web/global/post-signup-dialog | flags: CLASSNAME | new_name: Dialog title and aria-label use i18n bindings -->

### Requirement: Dialog title and aria-label use i18n bindings
All user-visible strings in the post-signup dialog SHALL use i18n translation bindings. No hardcoded display strings are permitted in the template.

#### Scenario: Title renders in active locale
- **WHEN** the post-signup dialog is displayed
- **AND** the active locale is `en`
- **THEN** the `<h2>` title SHALL render using the `postSignup.title` translation key in the EN translation
- **AND** the rendered text SHALL be in English (e.g., `Account registration complete!`)

#### Scenario: Title renders in Japanese locale
- **WHEN** the post-signup dialog is displayed
- **AND** the active locale is `ja`
- **THEN** the `<h2>` title SHALL render using the `postSignup.title` translation key in the JA translation
- **AND** the rendered text SHALL be `✅ アカウント登録完了！`

#### Scenario: aria-label follows active locale
- **WHEN** the post-signup dialog is displayed
- **AND** the active locale is `en`
- **THEN** the wrapping `<bottom-sheet>` element SHALL have an `aria-label` rendered from the `postSignup.ariaLabel` translation key in the EN translation

#### Scenario: Translation key parity
- **WHEN** `postSignup.title` or `postSignup.ariaLabel` keys exist in the Japanese translation resource
- **THEN** the same keys SHALL exist in the English translation resource
