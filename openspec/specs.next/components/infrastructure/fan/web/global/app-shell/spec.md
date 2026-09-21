# App Shell

## Purpose

Provides the application's outer shell: brand identity, page transition animations, runtime configuration loading, an authentication guard for protected routes, and a consistent layout frame with tactile interaction feedback throughout the app.

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

### Requirement: Page Shell Component
The system SHALL provide a `<page-shell>` custom element that standardizes the page layout structure across route pages, eliminating duplicated page-layout and page-header CSS.

#### Scenario: Standard page layout
- **WHEN** `<page-shell title-key="nav.tickets">` wraps page content
- **THEN** the component SHALL render a `<main>` element with page-layout styles
- **AND** a `<header>` with an `<h1>` using the i18n key via `t.bind`
- **AND** default slot content SHALL appear below the header

#### Scenario: Header actions slot
- **WHEN** a page provides content to the `header-actions` named slot
- **THEN** the content SHALL appear in the header row beside the title
- **AND** this SHALL support buttons, toggles, or count badges

#### Scenario: Hidden header
- **WHEN** `<page-shell show-header.bind="false">` is used
- **THEN** the header SHALL NOT be rendered
- **AND** the page content SHALL fill the entire layout area

#### Scenario: Pages excluded from page-shell
- **WHEN** a route page requires custom attributes on its `<main>` element (e.g., `data-search-mode.bind`)
- **THEN** that page SHALL NOT use `<page-shell>` and SHALL manage its own layout structure

---

### Requirement: `/config.json` SHALL conform to the runtime configuration schema

The runtime configuration document SHALL be a JSON object whose top-level shape exactly matches the app's runtime configuration schema. That schema SHALL be the single source of truth for the contract between the web app and any environment that serves `/config.json`. The schema fields SHALL include: `environment` (one of `dev | staging | prod`), `apiBaseUrl` (absolute https URL), `zitadelIssuer` (absolute https URL), `zitadelClientId` (non-empty string), `zitadelOrgId` (non-empty string), `vapidPublicKey` (non-empty string), `circuitBaseUrl` (string, MAY be empty when ZK circuits are unavailable in the environment), `previewArtistIds` (string array), `previewArtistNames` (string array, same length as `previewArtistIds`), and `logLevel` (one of `trace | debug | info | warn | error`). All fields except `circuitBaseUrl` (which MAY be empty) and the two `previewArtist*` arrays (which MAY be empty) are required-and-non-empty; the spec's "MAY be empty" carve-outs are exhaustive.

#### Scenario: Bootstrap validates required fields

- **WHEN** `/config.json` is fetched and parsed
- **AND** any of `apiBaseUrl`, `zitadelIssuer`, `zitadelClientId`, `zitadelOrgId`, `vapidPublicKey`, `environment`, or `logLevel` is missing, empty, or not a string of the expected shape
- **THEN** bootstrap SHALL throw an error naming the offending field
- **AND** the app SHALL NOT start
- **AND** the page SHALL render a minimal static error notice that surfaces the validation failure to the user

#### Scenario: Empty-string `circuitBaseUrl` disables ZK features

- **WHEN** `circuitBaseUrl` is present in the parsed config but is the empty string
- **THEN** bootstrap SHALL succeed (the field is required-present but MAY be empty per the schema)
- **AND** the zero-knowledge (ZK) proof feature SHALL treat the empty value as "circuits unavailable in this environment" and disable ZK features at the point of use without attempting any circuit fetch

#### Scenario: `previewArtistIds` and `previewArtistNames` length mismatch is rejected

- **WHEN** `/config.json` parses successfully
- **AND** `previewArtistIds.length` does not equal `previewArtistNames.length`
- **THEN** bootstrap SHALL throw an error naming the length-mismatch invariant
- **AND** the app SHALL NOT start
- **AND** the rendered error page SHALL state the observed lengths so the operator can correct the configuration

### Requirement: Bootstrap failures SHALL surface a static error page

When any failure occurs between the page load and `Aurelia.start()` (network failure on `/config.json`, JSON parse error, schema validation failure, or environment cross-check failure), the SPA SHALL replace the document body with a minimal static error page that identifies the failure category and (in non-production environments) the underlying error message. The error page SHALL NOT depend on any Aurelia-provided UI primitive.

#### Scenario: Network failure on /config.json shows error page

- **WHEN** `/config.json` fetch returns a non-2xx status or fails with a network error
- **THEN** the document body SHALL be replaced with a static error block
- **AND** the block SHALL include the literal text "App failed to start" or equivalent
- **AND** the block SHALL include the HTTP status or error class for diagnosis

#### Scenario: Schema validation failure shows error page

- **WHEN** `/config.json` parses successfully but fails the required-field validation
- **THEN** the document body SHALL be replaced with the static error block
- **AND** the block SHALL name the offending field

### Requirement: Auth hook guards all authenticated routes
The `AuthHook.canLoad` method SHALL enforce authentication on all routes except those with `data.auth === false`.

#### Scenario: Public route bypasses auth check
- **WHEN** `canLoad` is called with a route where `data.auth === false`
- **THEN** it SHALL return `true` without awaiting `authService.ready`

#### Scenario: Authenticated user on protected route
- **WHEN** `canLoad` is called for a protected route and `authService.isAuthenticated` is `true`
- **THEN** it SHALL return `true`

#### Scenario: Unauthenticated user redirected to welcome
- **WHEN** `canLoad` is called for a protected route and `authService.isAuthenticated` is `false`
- **THEN** it SHALL return the redirect path `/welcome`
- **AND** it SHALL show a toast notification

#### Scenario: Auth readiness is awaited before checking
- **WHEN** `canLoad` is called and `authService.ready` has not yet resolved
- **THEN** the method SHALL await `authService.ready` before checking `isAuthenticated`

### Requirement: Deduplicated auth token refresh on Unauthenticated errors

The auth retry interceptor SHALL intercept `Code.Unauthenticated` errors, attempt a silent OIDC token refresh, and retry the request. Concurrent `Unauthenticated` errors SHALL be deduplicated: if a token refresh is already in progress when another `Unauthenticated` error is received, the interceptor handling it SHALL await the in-progress refresh rather than issuing a new one, so that at most one refresh is initiated per expiry cycle.

#### Scenario: Silent refresh succeeds and request is retried
- **WHEN** a gRPC call returns `Code.Unauthenticated`
- **THEN** the interceptor SHALL call `signinSilent()` and retry the original request

#### Scenario: Silent refresh fails and user is redirected
- **WHEN** a gRPC call returns `Code.Unauthenticated` and `signinSilent()` throws
- **THEN** the interceptor SHALL redirect to `/welcome`

#### Scenario: Non-auth errors pass through
- **WHEN** a gRPC call returns an error code other than `Unauthenticated`
- **THEN** the interceptor SHALL re-throw the error without interception

#### Scenario: Single RPC gets Unauthenticated
- **WHEN** one RPC returns `Unauthenticated` and no refresh is in progress
- **THEN** the interceptor SHALL call `signinSilent()` and await the result
- **AND** on success, retry the original RPC with the new access token
- **AND** on failure, clear the user session and redirect to `/welcome`

#### Scenario: Multiple concurrent RPCs all get Unauthenticated
- **WHEN** two or more in-flight RPCs simultaneously receive `Unauthenticated`
- **THEN** exactly one `signinSilent()` request SHALL be sent to Zitadel
- **AND** all concurrent interceptors SHALL await the same refresh promise
- **AND** on success, each interceptor SHALL retry its original RPC with the new token
- **AND** on failure, the user session SHALL be cleared and the user redirected to `/welcome`

#### Scenario: Subsequent expiry after refresh completes
- **WHEN** a token refresh completes and the singleton promise is cleared
- **AND** the new access token later expires
- **THEN** the next `Unauthenticated` response SHALL start a new `signinSilent()` call

### Requirement: Immediate tactile acknowledgement on press

Tappable controls (buttons and interactive cards) across the app SHALL acknowledge a press within the short
motion band via a shared primitive: a contact-point ripple and a round↔squircle corner morph on `:active`,
using a spatial spring. The primitive SHALL be applied app-wide (not only in discovery) via a reusable
mechanism, and SHALL keep the clickable hit area stable while the visual shape morphs.

#### Scenario: Button press ripples and morphs

- **WHEN** a user presses a button or tappable card
- **THEN** a ripple originates at the contact point and the corner radius morphs with a spatial spring, then
  settles on release

#### Scenario: Hit target is preserved during morph

- **WHEN** the press-morph animates the visual shape
- **THEN** the interactive/clickable bounds remain unchanged and the target stays ≥ 44–48px

#### Scenario: Reduced motion still acknowledges

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the ripple/morph animation is suppressed but a non-motion acknowledgement (e.g. state-layer or
  opacity change) still confirms the tap

### Requirement: Haptic feedback for meaningful confirmations

The app SHALL provide a shared haptic feedback capability (generalized from the discovery orb) and invoke it
on meaningful confirm actions (e.g. follow/unfollow confirmation) where supported by the platform. Haptics
SHALL be feature-detected and degrade silently where unavailable (e.g. iOS Safari lacks the Web Vibration
API), and SHALL never be the sole feedback for an action.

#### Scenario: Confirm action triggers haptic where supported

- **WHEN** a user completes a meaningful confirm action on a device that supports vibration
- **THEN** a short haptic pulse fires in addition to the visual feedback

#### Scenario: Graceful degradation without vibration support

- **WHEN** the platform does not support the Web Vibration API
- **THEN** the action still completes with full visual feedback and no error

### Requirement: Synchronous prelude remains in loading()
The synchronous setup a menu-tab route performs before fetching — toggling `isLoading`, restoring filters from URL query params, hydrating persisted guest state, and computing banner visibility — SHALL run inside `loading()` before the fetch routine is invoked, so this state is correct on the first render. The request `AbortController` is owned by the fetch routine (see "Re-entrant load"), not created separately in the `loading()` body, so there is a single owner and the routine never aborts a controller the `loading()` body just created.

#### Scenario: Prelude state is set before first paint
- **WHEN** `loading()` runs for a menu-tab route
- **THEN** `isLoading`, URL-derived filters, hydrated guest state, and banner flags SHALL be assigned before the fetch routine is invoked
- **AND** the fetch routine's `AbortController` SHALL be created synchronously at the head of the routine (before its first await), so it exists before first paint
- **AND** the first render SHALL reflect that prelude state

#### Scenario: Re-entrant load aborts the prior request first
- **WHEN** a route's fetch routine runs while a previous request for that route is still in flight
- **THEN** the routine SHALL abort the previous `AbortController` and create a new one, then run the fetch with the new controller's signal (mirroring the existing `loadData()` pattern)
- **AND** a stale late response SHALL NOT overwrite state from the newer request

### Requirement: Overlay elements excluded from grid flow
All overlay custom elements (`pwa-install-prompt`, `notification-prompt`, `toast-notification`, `error-banner`, `coach-mark`) SHALL be removed from normal document flow so they do not create implicit CSS Grid rows in the `app-shell` shell layout. The bottom navigation bar and page header SHALL stay pinned even under a standalone PWA pull-to-refresh / overscroll gesture, because the document root is a non-scrolling frame and scrolling is confined to the single inner container.

#### Scenario: Bottom nav stays at viewport bottom
- **WHEN** the dashboard page has enough events to require scrolling (20+ concerts across multiple dates)
- **THEN** `bottom-nav-bar` SHALL remain visible and pinned at the bottom of the viewport at all times
- **AND** the `dashboard-route` CE SHALL constrain all descendants to viewport height via a 2-layer height chain: `dashboard-route` (grid, `block-size: 100%`) → `<main>` (scroll container, `overflow-block: auto`)
- **AND** no intermediate element between `au-viewport` and the scroll container SHALL have a rendered height exceeding the `au-viewport` height

#### Scenario: Bottom nav and header stay pinned after a pull-to-refresh gesture
- **WHEN** the app is running as an installed standalone PWA on the dashboard
- **AND** the user performs a pull-to-refresh / downward overscroll gesture
- **THEN** the bottom navigation bar SHALL remain visible and pinned at the bottom of the viewport
- **AND** the page header (the "Timetable" title row) SHALL remain visible and pinned at the top of the viewport
- **AND** the document root SHALL NOT scroll to make the header and the bottom nav bar mutually exclusive on screen

#### Scenario: Stage header stays fixed above scrollable content
- **WHEN** the user scrolls the concert list downward
- **THEN** the stage header (HOME STAGE / NEAR STAGE / AWAY STAGE) SHALL remain fixed above the scrollable content
- **AND** the stage header SHALL be a `<header>` element that is a direct child of `dashboard-route`, outside the `<main>` scroll container
- **AND** `dashboard-route` SHALL use CSS Grid with named areas via the `grid-template` shorthand: `"stage-home stage-near stage-away" auto` / `"lane-home lane-near lane-away" minmax(0, 1fr)` / `1fr 1fr 1fr`
- **AND** the stage header SHALL use `grid-template-columns: subgrid` with `grid-column: stage-home / stage-away` (named area implicit lines)
- **AND** the scroll container and all intermediate elements (`.concert-scroll`, `.date-group-list`, `li`, `.lane-grid`) SHALL use `grid-template-columns: subgrid` to propagate the 3-column layout from the root grid

#### Scenario: Scroll container is properly constrained
- **WHEN** concert data overflows the viewport
- **THEN** the `<main .concert-scroll>` element's `scrollHeight` SHALL be greater than its `clientHeight`
- **AND** the scroll container SHALL be the only scrollable element in the height chain
- **AND** the scroll container SHALL declare `overscroll-behavior: contain` so a scroll-boundary bounce does not chain into the document root

#### Scenario: Overlay elements remain functional
- **WHEN** an overlay element activates (e.g., toast notification, coach-mark spotlight)
- **THEN** the overlay SHALL render correctly via the browser top-layer API, unaffected by the flow removal

### Requirement: Document root is a non-scrolling frame
The document root (`html` and `body`) SHALL be a non-scrolling frame so that it is never a scroll source and native overscroll gestures (pull-to-refresh) in a standalone PWA cannot shift the shell chrome. All scrolling SHALL be confined to inner scroll containers.

#### Scenario: Root elements do not scroll
- **WHEN** the application is loaded in any route
- **THEN** `html` and `body` SHALL declare a definite height (`block-size: 100%`)
- **AND** `html` and `body` SHALL declare `overflow: hidden`
- **AND** `body` SHALL NOT declare `min-block-size: 100dvh` (or any rule that makes `body` taller than the visible viewport and thus a scroll source)
- **AND** the `app-shell` grid SHALL remain the single height owner at `block-size: 100dvh`

#### Scenario: Overscroll gesture does not chain to the document
- **WHEN** the user performs a pull-to-refresh or overscroll gesture in the installed standalone PWA
- **THEN** `html` and `body` SHALL declare `overscroll-behavior: none`
- **AND** the document SHALL NOT scroll, bounce, or trigger a native pull-to-refresh reload
- **AND** the bottom navigation bar and the page header SHALL both remain visible and pinned in their positions

#### Scenario: Inner scroll container contains its overscroll
- **WHEN** the user scrolls the concert list to its top or bottom boundary
- **THEN** the concert scroll container SHALL declare `overscroll-behavior: contain`
- **AND** the scroll SHALL NOT chain into the document root
