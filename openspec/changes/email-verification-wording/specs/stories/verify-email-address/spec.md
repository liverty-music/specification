## MODIFIED Requirements

### Requirement: A fan verifies their address from the email

After sign-up, a fan SHALL receive a verification email in their preferred language. Opening its link on any device and confirming SHALL verify the address without signing in, and SHALL offer a way into the app. Settings SHALL then show the address as verified on the fan's signed-in devices the next time Settings is opened or its tab is shown.

#### Scenario: Sign up, then verify on the phone

- **WHEN** a fan signs up in Japanese, opens the verification email on their phone and taps "メールアドレスを確認する"
- **THEN** the email was in Japanese, the screen says the address is verified, and Settings on their laptop shows 確認済み when they return to it
