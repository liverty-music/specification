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
The system SHALL conditionally show or hide the navigation bar based on the current route context. The navigation bar SHALL be an in-flow grid child of the app shell, not a fixed-position or top-layer element.

#### Scenario: App shell uses CSS Grid layout with height propagation
- **WHEN** the application shell renders
- **THEN** the root container SHALL use CSS Grid with `grid-template-rows: 1fr min-content`
- **AND** the container height SHALL be `100dvh` (dynamic viewport height)
- **AND** the `<main>` element SHALL occupy the `1fr` row and use CSS Grid (`grid-template-rows: auto auto 1fr`) to arrange prompts and the viewport
- **AND** the `<main>` element SHALL use `overflow: hidden` to prevent scrolling at the main level
- **AND** the `<au-viewport>` element SHALL occupy the `1fr` track within `<main>`, providing a definite height to route components
- **AND** the `<au-viewport>` element SHALL use `overflow-y: auto` as the scrolling container for route content
- **AND** route components SHALL use `min-height: 100%` to fill the viewport's height (not `100dvh` or `100vh`)
- **AND** the `<bottom-nav-bar>` element SHALL occupy the `min-content` row as a normal flow child
- **AND** the navigation bar SHALL NOT use `position: fixed`, `position: absolute`, or the Popover API (`popover` attribute / `showPopover()`)

#### Scenario: Navigation hidden during onboarding
- **WHEN** the user is on the Landing Page, Artist Discovery, or Loading Sequence routes
- **THEN** the system SHALL NOT display the bottom navigation bar
- **AND** the `1fr` row SHALL expand to fill the full `100dvh` height

#### Scenario: Navigation shown on dashboard
- **WHEN** the user is on the Dashboard or post-onboarding routes
- **THEN** the system SHALL display the bottom navigation bar in the `min-content` grid row
- **AND** the navigation bar SHALL include tab icons and labels for Home, Discover, My Artists, Tickets, and Settings

#### Scenario: Navigation remains visible beneath area setup dialog
- **WHEN** the first-visit area setup dialog is displayed on the Dashboard
- **THEN** the area setup dialog SHALL render via `<dialog>` `showModal()` in the browser's Top Layer
- **AND** the bottom navigation bar SHALL remain in its normal grid position beneath the Top Layer
- **AND** the `::backdrop` pseudo-element SHALL visually dim the entire page including the navigation bar

#### Scenario: Pages do not compensate for navigation bar height
- **WHEN** any route component renders inside the `<au-viewport>` element
- **THEN** the route component SHALL NOT apply viewport-relative height constraints (e.g., `100dvh`, `100vh`) or bottom padding (e.g., `pb-14`) to account for the navigation bar
- **AND** the CSS Grid layout SHALL ensure the route content fills the available space within the `1fr` track

---

### Requirement: Page Transition Animations
The system SHALL animate transitions between routes to provide visual continuity.

#### Scenario: Forward navigation transition
- **WHEN** the user navigates from one route to another
- **THEN** the outgoing page SHALL fade out (opacity 1->0)
- **AND** the incoming page SHALL fade in with a subtle upward slide (opacity 0->1, translateY 20px->0)
- **AND** the total transition duration SHALL be 250-350ms with ease-out timing

#### Scenario: Backward navigation transition
- **WHEN** the user navigates back (browser back or in-app back action)
- **THEN** the outgoing page SHALL fade out with a subtle downward slide (opacity 1->0, translateY 0->20px)
- **AND** the incoming page SHALL fade in (opacity 0->1)
- **AND** the total transition duration SHALL match the forward transition (250-350ms with ease-out timing)

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

---

### Requirement: Notification Prompt Placement

The notification prompt SHALL be rendered at the app shell level (`my-app.html`) rather than within the dashboard route template. This ensures the prompt is available on any post-onboarding route, not only the dashboard.

#### Scenario: Notification prompt rendered in app shell when eligible

- **WHEN** the user is authenticated (`auth.isAuthenticated === true`)
- **AND** onboarding is completed (`onboarding.isCompleted === true`)
- **AND** the navigation bar is visible (`showNav === true`)
- **THEN** the system SHALL render the `<notification-prompt>` component in the app shell
- **AND** the prompt SHALL appear above the main content area, below any app-level banners

#### Scenario: Notification prompt hidden during onboarding routes

- **WHEN** the user is on a fullscreen route (Landing Page, Loading Sequence, Auth Callback)
- **OR** the user is not authenticated
- **OR** onboarding is not completed
- **THEN** the system SHALL NOT render the `<notification-prompt>` component

#### Scenario: Notification prompt removed from dashboard route

- **WHEN** the dashboard route template is rendered
- **THEN** the template SHALL NOT contain a `<notification-prompt>` element
- **AND** the notification prompt import SHALL be removed from the dashboard template

---

### Requirement: PWA Install Prompt i18n

The PWA install prompt SHALL use i18n keys for all user-facing text, consistent with the notification prompt's existing i18n pattern.

#### Scenario: PWA install prompt displays localized text

- **WHEN** the PWA install prompt is visible
- **THEN** the title text SHALL be rendered via the `pwa.title` i18n key
- **AND** the description text SHALL be rendered via the `pwa.description` i18n key
- **AND** the install button label SHALL be rendered via the `pwa.install` i18n key
- **AND** the dismiss button label SHALL be rendered via the `pwa.notNow` i18n key
- **AND** the text SHALL NOT be hardcoded in the template

---

### Requirement: Prompt Entrance and Exit Animations

The PWA install prompt and notification prompt SHALL animate when entering and leaving the viewport, providing visual continuity with the rest of the onboarding flow.

#### Scenario: Prompt entrance animation

- **WHEN** the PWA install prompt or notification prompt becomes visible
- **THEN** the prompt SHALL animate in using a fade-slide-up effect (opacity 0 -> 1, translateY 16px -> 0)
- **AND** the animation duration SHALL be 600ms with ease-out timing
- **AND** the animation SHALL reuse the existing `fade-slide-up` keyframe defined in `my-app.css`

#### Scenario: Prompt exit animation

- **WHEN** the PWA install prompt or notification prompt is dismissed
- **THEN** the prompt SHALL animate out using a fade-slide-down effect (opacity 1 -> 0, translateY 0 -> 16px)
- **AND** the animation duration SHALL be 600ms with ease-out timing
- **AND** the element SHALL remain in the DOM until the exit animation completes

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the prompt entrance and exit animations SHALL be skipped
- **AND** the prompt SHALL appear and disappear instantly

