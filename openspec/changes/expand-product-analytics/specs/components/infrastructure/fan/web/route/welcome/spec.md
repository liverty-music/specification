## ADDED Requirements

### Requirement: Starting onboarding and starting sign-up are reported

The landing page SHALL send one usage analytics event when a visitor taps `[Get Started]`, and one when a visitor starts sign-up or sign-in from the page, just before the app leaves for hosted login, stating which of the two was started.

#### Scenario: Get Started
- **WHEN** a guest taps `[Get Started]`
- **THEN** one onboarding-started event is sent

#### Scenario: Sign-up from the landing page
- **WHEN** a guest starts sign-up from the landing page
- **THEN** one sign-up-started event is sent before the app leaves for hosted login
