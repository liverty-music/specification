# Capability: Signup Prompt Banner

## Purpose

Provide a persistent inline banner on My Artists and Dashboard pages prompting unauthenticated users to create an account, dismissed automatically on signup completion.

## ADDED Requirements

### Requirement: Inline Signup Banner on My Artists

The My Artists page SHALL display a persistent inline banner at the end of the artist list prompting unauthenticated users to sign up.

#### Scenario: Banner appears for unauthenticated users

- **WHEN** an unauthenticated user views the My Artists page
- **AND** the user has dismissed the notification dialog with "あとで" (or has completed onboarding without signup)
- **THEN** the system SHALL display an inline banner after the last artist row
- **AND** the banner SHALL display: "🔔 通知を有効にするには [アカウント作成]"
- **AND** the [アカウント作成] button SHALL initiate the Zitadel OIDC Passkey flow

#### Scenario: Banner not shown for authenticated users

- **WHEN** an authenticated user views the My Artists page
- **THEN** the signup banner SHALL NOT be rendered

#### Scenario: Banner disappears after signup

- **WHEN** the user completes signup (isAuthenticated becomes true)
- **THEN** the signup banner SHALL be removed from the DOM

### Requirement: Inline Signup Banner on Dashboard

The Dashboard page SHALL display a persistent inline banner prompting unauthenticated users to sign up.

#### Scenario: Banner appears on dashboard for unauthenticated users

- **WHEN** an unauthenticated user views the Dashboard
- **AND** the user has completed onboarding (onboardingStep >= 7) or has dismissed the notification dialog
- **THEN** the system SHALL display an inline banner after the lane grid content
- **AND** the banner SHALL display: "🔔 ライブ通知を受け取ろう [アカウント作成]"
- **AND** the [アカウント作成] button SHALL initiate the Zitadel OIDC Passkey flow

#### Scenario: Banner not shown during onboarding steps 1-4

- **WHEN** the user is at onboarding steps 1 through 4
- **THEN** the dashboard signup banner SHALL NOT be rendered

#### Scenario: Banner not shown for authenticated users on dashboard

- **WHEN** an authenticated user views the Dashboard
- **THEN** the signup banner SHALL NOT be rendered

### Requirement: Shared Banner Component

The signup prompt banner SHALL be implemented as a shared component reusable across pages.

#### Scenario: Component renders consistently

- **WHEN** the signup-prompt-banner component is used on different pages
- **THEN** the visual style SHALL be consistent (same padding, typography, button style)
- **AND** the component SHALL accept a `message` attribute for page-specific copy
- **AND** the component SHALL be part of the scroll content (not sticky/fixed)
