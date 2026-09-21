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
- **THEN** the system SHALL display a brand favicon in the browser tab, served as PNG and ICO assets (no SVG favicon is required)
- **AND** the system SHALL provide an `apple-touch-icon` PNG for the iOS home screen
- **AND** the system SHALL provide a web app manifest with themed PNG icons (including a maskable variant) for Android and other PWA-compliant platforms
- **AND** the web app manifest SHALL NOT reference SVG icon assets

#### Scenario: Web app manifest declares the service name
- **WHEN** the web app manifest is served
- **THEN** the manifest `name` member SHALL be "Liverty Music"
- **AND** the manifest `short_name` member SHALL be "LivertyMusic"
- **AND** the `short_name` SHALL NOT be an abbreviation that omits part of the service name (e.g. "Liverty")
- **AND** consequently the installed PWA home-screen icon label SHALL present the service name rather than an abbreviation

#### Scenario: Theme color is consistent across HTML and manifest
- **WHEN** the application is loaded
- **THEN** the `theme-color` declared in the HTML `<head>` meta tag SHALL equal the `theme_color` declared in the web app manifest

### Requirement: Conditional Navigation Display
The system SHALL conditionally show or hide the navigation bar based on the current route context. The navigation bar SHALL be visible on all pages except the Landing Page and auth callback. The shell-hosted page header SHALL follow the same visibility condition as the navigation bar.

#### Scenario: App shell uses CSS Grid layout with named areas
- **WHEN** the application shell renders
- **THEN** the root container SHALL use CSS Grid with `grid-template-areas: "header" "viewport" "nav"` and `grid-template-rows: auto 1fr auto`
- **AND** the container height SHALL be `100dvh` (dynamic viewport height)
- **AND** the shell-hosted `<page-header>` SHALL occupy the `header` area
- **AND** `<au-viewport>` SHALL be a direct child of the root container (no intermediate wrapper div) and SHALL be explicitly assigned `grid-area: viewport`
- **AND** `<au-viewport>` SHALL receive ONLY grid-area placement from `app-shell.css` (no other layout styling) — its block-size is determined by the `viewport` row's grid stretch. The explicit placement is required so the viewport never auto-places into the `auto` `header` row when the header/nav are hidden (which would collapse the route to zero block-size)
- **AND** `<bottom-nav-bar>` SHALL be explicitly assigned `grid-area: nav`
- **AND** the navigation bar SHALL NOT use `position: fixed`, `position: absolute`, or the Popover API

#### Scenario: Navigation hidden on Landing Page and auth callback only
- **WHEN** the user is on the Landing Page or Auth Callback route
- **THEN** the system SHALL NOT display the bottom navigation bar
- **AND** the system SHALL NOT display the shell-hosted page header
- **AND** the `1fr` viewport row SHALL expand to fill the full `100dvh` height

#### Scenario: Navigation shown during onboarding (discover, dashboard, my-artists)
- **WHEN** the user is on the Artist Discovery, Dashboard, or My Artists route during onboarding
- **THEN** the system SHALL display the bottom navigation bar
- **AND** navigation SHALL be restricted by the existing route guards (`AuthHook.canLoad()`)
- **AND** the system SHALL NOT apply additional click prevention on the navigation bar

#### Scenario: Navigation shown on post-onboarding routes
- **WHEN** the user is on the Dashboard or post-onboarding routes
- **THEN** the system SHALL display the bottom navigation bar in the `nav` grid area
- **AND** the navigation bar SHALL include tab icons and labels for Home, Discover, My Artists, Tickets, and Settings

#### Scenario: Navigation remains visible beneath area setup dialog
- **WHEN** the first-visit area setup dialog is displayed on the Dashboard
- **THEN** the area setup dialog SHALL render via `<dialog>` `showModal()` in the browser's Top Layer
- **AND** the bottom navigation bar SHALL remain in its normal grid position beneath the Top Layer
- **AND** the `::backdrop` pseudo-element SHALL visually dim the entire page including the navigation bar

#### Scenario: Dashboard icon data attribute for coach mark targeting
- **WHEN** the bottom navigation bar renders
- **THEN** the Dashboard tab link SHALL include a `data-nav-dashboard` attribute
- **AND** the My Artists tab link SHALL include a `data-nav-my-artists` attribute

#### Scenario: Pages do not compensate for navigation bar height
- **WHEN** any route component renders inside the `<au-viewport>` element
- **THEN** the route component SHALL NOT apply viewport-relative height constraints (e.g., `100dvh`, `100vh`) or bottom padding (e.g., `pb-14`) to account for the navigation bar
- **AND** the CSS Grid layout SHALL ensure the route content fills the available space within the `1fr` track

---

### Requirement: Stale-data warning uses overlay pattern
The dashboard stale-data warning SHALL render as a fixed-position overlay, consistent with the application's notification pattern (`toast-notification`, `error-banner`).

#### Scenario: Stale banner appears as fixed overlay
- **WHEN** the dashboard data reload fails and previous data exists (`isStale === true`)
- **THEN** the stale-data warning SHALL render as a `position: fixed` element at the top of the viewport
- **AND** the warning SHALL NOT occupy a grid row in the dashboard layout
- **AND** the warning SHALL appear above page content but below top-layer elements (dialogs, popovers)

#### Scenario: Stale banner does not affect scroll behavior
- **WHEN** the stale-data warning is visible
- **THEN** the `live-highway` scroll area SHALL occupy the full `main` grid area
- **AND** scrolling the concert list SHALL NOT move the stale-data warning

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

- **WHEN** the user is on a fullscreen route (Landing Page, Auth Callback)
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

### Requirement: App shell hosts the global FAB action launcher

The app shell SHALL host a single global FAB action launcher (see the
`fab-action-launcher` capability) as a top-layer surface alongside the bottom
navigation bar. The launcher SHALL be a single instance owned by the shell (not
re-created per route). The launcher SHALL be shown only when the bottom navigation
bar is shown; on routes that hide the navigation bar (Landing Page, Auth Callback)
the launcher SHALL NOT be rendered. So the launcher can float clear of the
navigation bar, the shell SHALL make the navigation bar's rendered height available
to the launcher (e.g. as a CSS custom property) rather than relying on a hard-coded
offset.

#### Scenario: Launcher present with the navigation bar

- **WHEN** the app shell renders a route that shows the bottom navigation bar
- **THEN** the shell SHALL render exactly one FAB action launcher instance in the top layer
- **AND** the launcher SHALL be positioned clear of the navigation bar using the navigation bar's published height plus the safe-area inset

#### Scenario: Launcher absent on fullscreen routes

- **WHEN** the user is on the Landing Page or Auth Callback route
- **THEN** the shell SHALL NOT render the FAB action launcher

#### Scenario: Navigation height is published for offset

- **WHEN** the bottom navigation bar is rendered
- **THEN** its rendered height SHALL be exposed to the launcher (e.g. via a CSS custom property on the shell)
- **AND** the launcher's bottom offset SHALL be derived from that height plus the bottom safe-area inset, without a hard-coded pixel constant

### Requirement: Instant page-identity switch on navigation intent

The system SHALL switch page identity — the page header title and the active
bottom-nav tab — at navigation intent, independent of the incoming route's
loading and entrance transition. Page identity SHALL be driven by a single
shared reactive state that both the shell-hosted page header and the bottom
navigation bar read from, and SHALL NOT be derived by reading the router's route
tree directly in the navigation bar.

The shared state SHALL be updated optimistically when navigation begins,
confirmed when navigation completes, and rolled back if navigation fails, so the
tap is acknowledged immediately while content continues to load or animate.

#### Scenario: Header title and active tab switch on tap before content loads
- **WHEN** the user taps a bottom-nav tab
- **THEN** the bottom-nav highlight SHALL move to the tapped tab immediately, before the incoming route's content has attached or finished its entrance transition
- **AND** the page header title SHALL change to the target page's title in the same immediate step
- **AND** the previous page's content MAY still be visible or animating out during this step

#### Scenario: Optimistic switch on navigation start
- **WHEN** an `au:router:navigation-start` event fires (from a tap, an in-app link, a programmatic load, or browser back/forward)
- **THEN** the shared page-identity state SHALL be set from the target route so the header title and active tab reflect the destination immediately

#### Scenario: Confirmation on navigation end
- **WHEN** an `au:router:navigation-end` event fires
- **THEN** the shared page-identity state SHALL be reconciled to the resolved current route
- **AND** the reconciled value SHALL take precedence over the optimistic value so redirects, fallback routes, and dynamic titles are reflected correctly

#### Scenario: Rollback on navigation error
- **WHEN** an `au:router:navigation-error` event fires
- **THEN** the shared page-identity state SHALL be restored to the last confirmed page identity
- **AND** the header title and active tab SHALL match the route that remains displayed

#### Scenario: Header and nav are not gated by the content transition
- **WHEN** the incoming route content performs its entrance transition (fade/slide)
- **THEN** the page header and the bottom navigation bar SHALL NOT be subject to that transition
- **AND** the header title and active tab SHALL already reflect the target page while the content transition is still in progress

#### Scenario: Dynamic route titles update the shared state
- **WHEN** a route changes its own title while it is the active route (e.g. the dashboard My Timetable ↔ All Nearby swap)
- **THEN** the route SHALL update the shared page-identity state
- **AND** the shell-hosted page header SHALL reflect the new title, preserving any opted-in title View-Transition morph
