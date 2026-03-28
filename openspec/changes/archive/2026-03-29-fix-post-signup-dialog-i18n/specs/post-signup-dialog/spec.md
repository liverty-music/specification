## ADDED Requirements

### Requirement: PostSignupDialog title and aria-label use i18n bindings
All user-visible strings in the PostSignupDialog component SHALL use `@aurelia/i18n` `t` attribute bindings. No hardcoded display strings are permitted in the template.

#### Scenario: Title renders in active locale
- **WHEN** the PostSignupDialog is displayed
- **AND** the active locale is `en`
- **THEN** the `<h2>` title SHALL render using the `postSignup.title` translation key in the EN translation
- **AND** the rendered text SHALL be in English (e.g., `Account registration complete!`)

#### Scenario: Title renders in Japanese locale
- **WHEN** the PostSignupDialog is displayed
- **AND** the active locale is `ja`
- **THEN** the `<h2>` title SHALL render using the `postSignup.title` translation key in the JA translation
- **AND** the rendered text SHALL be `✅ アカウント登録完了！`

#### Scenario: aria-label follows active locale
- **WHEN** the PostSignupDialog is displayed
- **AND** the active locale is `en`
- **THEN** the wrapping `<bottom-sheet>` element SHALL have an `aria-label` rendered from the `postSignup.ariaLabel` translation key in the EN translation

#### Scenario: Translation key parity
- **WHEN** `postSignup.title` or `postSignup.ariaLabel` keys exist in `ja/translation.json`
- **THEN** the same keys SHALL exist in `en/translation.json`
