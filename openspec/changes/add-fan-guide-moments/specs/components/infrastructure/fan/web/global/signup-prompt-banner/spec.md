# Delta for signup-prompt-banner

## MODIFIED Requirements

### Requirement: Guest Signup Prompt Banner

The system SHALL display a non-modal signup prompt banner to guest users after onboarding completion. The banner copy SHALL fit on one line next to its button on mobile and SHALL be consistent in intent across English and Japanese locales, and SHALL name what an account brings: notifications of new concerts. The button SHALL read "Sign Up" in both locales.

#### Scenario: Banner copy — Japanese

- **WHEN** the signup prompt banner is displayed to a guest user in Japanese locale
- **THEN** the banner SHALL display: 「新着ライブを通知で受け取ろう！」
- **AND** the banner SHALL include a [Sign Up] CTA button

#### Scenario: Banner copy — English

- **WHEN** the signup prompt banner is displayed to a guest user in English locale
- **THEN** the banner SHALL display: "Get new concerts by notification!"
- **AND** the banner SHALL include a [Sign Up] CTA button
