# App Shell Layout

## Purpose

Defines the application shell structure including brand identity, conditional navigation display, page transition animations, and authentication status UI. The app shell provides the consistent outer frame for all routes in the Liverty Music application.

## Requirements

### Requirement: Brand Identity Elements
The system SHALL display proper brand identity elements across the application.

#### Scenario: Page title displays service name
- **WHEN** any page is loaded
- **THEN** the HTML `<title>` SHALL include "Liverty Music" (e.g., "Liverty Music" or "Liverty Music - [Page Name]")
- **AND** the system SHALL NOT display default scaffold or template names (e.g., "Aurelia", "Vite", "React App")

#### Scenario: Favicon and PWA icons
- **WHEN** the application is loaded
- **THEN** the system SHALL display a brand favicon in the browser tab
- **AND** the system SHALL provide apple-touch-icon for iOS home screen
- **AND** the system SHALL provide a web app manifest with themed icons (including maskable versions) for Android and other PWA-compliant platforms

---

### Requirement: Conditional Navigation Display
The system SHALL conditionally show or hide the navigation bar based on the current route context.

#### Scenario: Navigation hidden during onboarding
- **WHEN** the user is on the Landing Page, Artist Discovery, or Loading Sequence routes
- **THEN** the system SHALL NOT display the top navigation bar
- **AND** the full viewport SHALL be available for the onboarding content

#### Scenario: Navigation shown on dashboard
- **WHEN** the user is on the Dashboard or post-onboarding routes
- **THEN** the system SHALL display a minimal, dark-themed navigation bar
- **AND** the navigation bar SHALL include the service logo and user account controls

---

### Requirement: Page Transition Animations
The system SHALL animate transitions between routes to provide visual continuity.

#### Scenario: Forward navigation transition
- **WHEN** the user navigates from one route to another
- **THEN** the outgoing page SHALL fade out (opacity 1->0)
- **AND** the incoming page SHALL fade in with a subtle upward slide (opacity 0->1, translateY 20px->0)
- **AND** the total transition duration SHALL be 250-350ms with ease-out timing

#### Scenario: Reduced motion preference
- **WHEN** the user has `prefers-reduced-motion: reduce` enabled in their OS/browser settings
- **THEN** the system SHALL skip all page transition animations
- **AND** route changes SHALL occur instantly

---

### Requirement: Auth Status UI Redesign
The system SHALL display authentication status with a cohesive, dark-themed design.

#### Scenario: Authenticated user display
- **WHEN** a user is authenticated
- **THEN** the system SHALL display the user's name in a compact format
- **AND** the sign-out control SHALL use a subtle, secondary-styled button (not a red button)
- **AND** the overall auth UI SHALL use the design system's color tokens

#### Scenario: Unauthenticated user display
- **WHEN** no user is authenticated and the navigation bar is visible
- **THEN** the system SHALL display a single "Sign In" button using the brand accent color
