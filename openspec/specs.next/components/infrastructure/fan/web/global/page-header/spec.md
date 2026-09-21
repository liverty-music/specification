# Page Header

## Purpose

Provides the reusable page header shown across routes, rendering the localized page title and optional trailing actions, switching instantly on navigation, and showing authentication status.

## Requirements

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

### Requirement: Page header renders i18n title
The `page-header` CE SHALL render a `<header>` element containing an `<h1>` whose text content is resolved from the `title-key` bindable via the i18n `t` binding.

#### Scenario: Title-only header (settings, tickets)
- **WHEN** `<page-header title-key="settings.title"></page-header>` is used with no slot content
- **THEN** the header renders `<h1>` with the translated text for `settings.title` and no additional child elements

#### Scenario: Title key changes dynamically
- **WHEN** the `title-key` bindable value changes at runtime
- **THEN** the `<h1>` text updates to reflect the new translation

### Requirement: Page header supports trailing actions via slot
The `page-header` CE SHALL provide a default `<au-slot>` after the `<h1>` element for optional trailing content (badges, buttons).

#### Scenario: Header with slotted actions (my-artists)
- **WHEN** `<page-header title-key="nav.myArtists"><span class="artist-count">(...)</span><button>...</button></page-header>` is used
- **THEN** the `<h1>` is followed by the slotted `<span>` and `<button>`, laid out inline via flexbox with the title taking remaining space

#### Scenario: No slot content provided
- **WHEN** `<page-header title-key="nav.tickets"></page-header>` is used without children
- **THEN** the header renders only the `<h1>` with no extra whitespace or empty wrapper

### Requirement: Page header provides consistent visual styling
The `page-header` CE SHALL encapsulate the shared header styles: padding, bottom border, background color, and `<h1>` typography (font-family, size, weight, letter-spacing).

#### Scenario: Visual consistency across routes
- **WHEN** `page-header` is rendered in my-artists, settings, and tickets routes
- **THEN** all three headers share identical padding (`--space-xs`), border (`1px solid` at 10% white), background (`--color-surface-raised`), and `<h1>` typography

### Requirement: Page header participates in route grid layout
The `page-header` CE host element SHALL set `grid-area: header` so it integrates with the app shell's `grid-template-areas` without additional route-level CSS.

#### Scenario: Header placed in grid area
- **WHEN** the app shell defines `grid-template-areas: "header" "viewport" "nav"`
- **THEN** the `page-header` CE SHALL occupy the `header` grid area of the shell automatically
- **AND** no route-level CSS SHALL be required to position the header

### Requirement: Page header is globally registered
The `<page-header>` custom element SHALL be registered globally so all routes can use it without per-route `<import>` statements.

#### Scenario: Usage without explicit import
- **WHEN** a route template uses `<page-header title-key="...">` without an `<import>` tag
- **THEN** the component resolves and renders correctly

### Requirement: Page header is a single shell-hosted instance bound to shared state
The `page-header` CE SHALL be rendered as a single persistent instance owned by the app shell (not one instance per route), and its `title-key` and `morph-title` bindables SHALL be bound to the shared page-identity state rather than authored per route. As the shared state changes, the header SHALL update in place without being unmounted and remounted across route changes.

#### Scenario: Single shell-hosted instance across route changes
- **WHEN** the user navigates between routes that show the navigation bar
- **THEN** the same `page-header` instance SHALL remain mounted in the shell
- **AND** its `<h1>` text SHALL update from the shared state's current title key without the element being destroyed and recreated

#### Scenario: Title bound to shared state, not per-route markup
- **WHEN** a route becomes active
- **THEN** the header title SHALL be sourced from the shared page-identity state
- **AND** no route template SHALL author its own `<page-header>` element to supply the title

#### Scenario: Title morph preserved for in-place title swaps
- **WHEN** the shared state's title changes while the header stays mounted and `morph-title` is enabled (e.g. the dashboard My Timetable ↔ All Nearby swap)
- **THEN** the `<h1>` SHALL carry the stable `view-transition-name` so the title text can morph across a same-document View Transition
