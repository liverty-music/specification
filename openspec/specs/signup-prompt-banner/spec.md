# Capability: Signup Prompt Banner

## Purpose

Provide a persistent inline banner on My Artists and Dashboard pages prompting unauthenticated users to create an account, dismissed automatically on signup completion.

## Requirements

### Requirement: Inline Signup Banner on My Artists

The My Artists page SHALL display a persistent inline banner at the end of the artist list prompting unauthenticated users to sign up.

#### Scenario: Banner appears for unauthenticated users

- **WHEN** an unauthenticated user views the My Artists page
- **AND** the user has completed onboarding (`onboarding.isCompleted` is true)
- **THEN** the system SHALL display the signup-prompt-banner
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
- **AND** the component SHALL be fixed-positioned above the bottom navigation bar

#### Scenario: Banner has frosted glass background

- **WHEN** the signup-prompt-banner is rendered
- **THEN** the banner background SHALL use a frosted glass surface (dark base at 85% opacity with backdrop blur)
- **AND** the top border SHALL display a 2px gradient from `--color-brand-primary` to `--color-brand-secondary`

#### Scenario: CTA button has glow pulse animation

- **WHEN** the signup-prompt-banner is rendered
- **AND** the user has not set `prefers-reduced-motion: reduce`
- **THEN** the "Create Account" button SHALL display a continuous glow pulse animation using `--color-brand-primary` as the glow color
- **AND** the animation SHALL cycle every 2.5 seconds with ease-in-out timing

#### Scenario: CTA button has no animation for reduced motion

- **WHEN** the signup-prompt-banner is rendered
- **AND** the user has set `prefers-reduced-motion: reduce`
- **THEN** the "Create Account" button SHALL NOT display the glow pulse animation

#### Scenario: Banner slides in on appearance

- **WHEN** the signup-prompt-banner becomes visible
- **AND** the user has not set `prefers-reduced-motion: reduce`
- **THEN** the banner SHALL animate in from below with a slide-up and fade-in transition over 400ms

#### Scenario: Banner appears instantly for reduced motion

- **WHEN** the signup-prompt-banner becomes visible
- **AND** the user has set `prefers-reduced-motion: reduce`
- **THEN** the banner SHALL appear immediately without animation

### Requirement: Dashboard auth guard for journey fetch

The Dashboard SHALL NOT call authenticated RPC endpoints when the user is unauthenticated.

#### Scenario: Journey data skipped for unauthenticated users

- **WHEN** an unauthenticated user views the Dashboard
- **THEN** the system SHALL NOT call `TicketJourneyService/ListByUser`
- **AND** the system SHALL use an empty journey map as fallback
- **AND** no 401 errors SHALL appear in the browser console

#### Scenario: Journey data fetched for authenticated users

- **WHEN** an authenticated user views the Dashboard
- **THEN** the system SHALL call `TicketJourneyService/ListByUser` to populate ticket journey statuses
