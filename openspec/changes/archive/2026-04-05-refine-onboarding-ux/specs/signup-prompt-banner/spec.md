## MODIFIED Requirements

### Requirement: Guest Signup Prompt Banner
The system SHALL display a non-modal signup prompt banner to guest users after onboarding completion. The banner copy SHALL be concise (≤2 lines on mobile) and SHALL be consistent in intent across English and Japanese locales.

#### Scenario: Banner copy — Japanese
- **WHEN** the signup prompt banner is displayed to a guest user in Japanese locale
- **THEN** the banner SHALL display: "フォロー情報を保存してコンサート通知を受け取ろう！"
- **AND** the banner SHALL include a [アカウント作成] CTA button

#### Scenario: Banner copy — English
- **WHEN** the signup prompt banner is displayed to a guest user in English locale
- **THEN** the banner SHALL display: "Save your followed artists and get concert notifications."
- **AND** the banner SHALL include a [Create Account] CTA button
