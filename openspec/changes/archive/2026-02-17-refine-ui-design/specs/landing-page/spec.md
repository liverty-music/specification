## MODIFIED Requirements

### Requirement: Landing Page Hero Display
The system SHALL display a landing page with a compelling value proposition and immersive dark-themed design when an unauthenticated user visits the root URL.

#### Scenario: First-time visitor sees hero content
- **WHEN** an unauthenticated user navigates to `/`
- **THEN** the system SHALL display a hero heading with the text "大好きなあのバンドのライブ、もう二度と見逃さない。"
- **AND** the system SHALL display a sub-heading with the text "あなたの推しアーティストを登録するだけで、全国のライブ日程を自動収集。"
- **AND** the page SHALL be optimized for mobile portrait orientation
- **AND** the page SHALL use a dark gradient background consistent with the design system's surface palette
- **AND** the hero heading SHALL use the display font at mega size (text-4xl or larger)
- **AND** the service logo or wordmark SHALL be displayed above the hero copy

#### Scenario: Hero entrance animation
- **WHEN** the landing page is first rendered
- **THEN** the hero heading SHALL fade in with a subtle upward slide animation (300-500ms delay)
- **AND** the sub-heading SHALL fade in after the heading (staggered by 200ms)
- **AND** the CTA button SHALL fade in after the sub-heading (staggered by 200ms)

### Requirement: Passkey Authentication CTA
The system SHALL provide "Sign Up" and "Sign In" buttons with visually prominent, branded styling that triggers Passkey authentication via Zitadel.

#### Scenario: New user initiates sign-up
- **WHEN** an unauthenticated user clicks the "Sign Up" button
- **THEN** the system SHALL initiate the Zitadel OIDC flow with `prompt=create` to default to the registration form
- **AND** Zitadel SHALL handle Passkey registration via its hosted UI

#### Scenario: Returning user initiates sign-in
- **WHEN** an unauthenticated user clicks the "Sign In" button
- **THEN** the system SHALL initiate the Zitadel OIDC flow for Passkey authentication

#### Scenario: CTA button visual styling
- **WHEN** the landing page is displayed
- **THEN** the primary CTA (Sign Up) SHALL use the brand accent color with a glow/shadow effect
- **AND** the secondary CTA (Sign In) SHALL use a ghost/outline style with the brand color
- **AND** both buttons SHALL have rounded corners using the design system's button radius token

#### Scenario: No alternative auth methods displayed
- **WHEN** the landing page is displayed
- **THEN** the system SHALL NOT display email/password fields or social login buttons (Google, Spotify, etc.)
- **AND** Passkey SHALL be the sole authentication method

### Requirement: Authenticated User Redirect
The system SHALL redirect already-authenticated users away from the landing page.

#### Scenario: Authenticated user visits landing page
- **WHEN** an authenticated user navigates to `/`
- **THEN** the system SHALL check whether the user has completed onboarding (has ≥1 followed artist)
- **AND** if onboarding is incomplete, the system SHALL redirect to the Artist Discovery page
- **AND** if onboarding is complete, the system SHALL redirect to the Dashboard

### Requirement: Mobile-First Layout
The system SHALL render the landing page with a mobile-first responsive design.

#### Scenario: Mobile viewport rendering
- **WHEN** the landing page is accessed on a smartphone (viewport width < 768px)
- **THEN** the system SHALL center the hero content vertically and horizontally
- **AND** the CTA button SHALL be full-width with adequate touch target size (minimum 48px height)
- **AND** the system SHALL NOT produce horizontal scrolling
