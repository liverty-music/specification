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

### Requirement: Page identity follows the displayed route

The page header title and the active bottom-nav tab SHALL always describe the
route that is displayed. Both SHALL be taken from that route's own
configuration, so there is one source of page identity for the whole app and
no second copy of it to keep in step. They SHALL change when a navigation
completes. A navigation that fails or is cancelled leaves the previous route
displayed, and its identity SHALL remain on screen unchanged.

#### Scenario: Header title and active tab match the route shown

- **WHEN** the fan taps a bottom-nav tab and the target route is displayed
- **THEN** the page header SHALL show that route's title
- **AND** the bottom-nav highlight SHALL be on that route's tab

#### Scenario: A failed navigation leaves identity unchanged

- **WHEN** a navigation fails or is cancelled and the previous route remains
  displayed
- **THEN** the page header title and the active tab SHALL still be those of the
  previous route
- **AND** at no point SHALL they have shown the failed target

#### Scenario: Redirects and the fallback route are reflected

- **WHEN** a navigation resolves to a different route than the one requested
  (a redirect, or the not-found fallback)
- **THEN** the page header title and the active tab SHALL be those of the route
  actually displayed

#### Scenario: Routes without a title show no header

- **WHEN** the displayed route declares no page title (legal documents, About,
  not-found)
- **THEN** no page header SHALL be rendered

### Requirement: Page header is a single shell-hosted instance bound to the displayed route
The `page-header` CE SHALL be rendered as a single persistent instance owned by the app shell (not one instance per route), and its title SHALL be bound to the displayed route's configured title rather than authored per route. As the displayed route changes, the header SHALL update in place without being unmounted and remounted across route changes.

#### Scenario: Single shell-hosted instance across route changes
- **WHEN** the user navigates between routes that show the navigation bar
- **THEN** the same `page-header` instance SHALL remain mounted in the shell
- **AND** its `<h1>` text SHALL update to the displayed route's title without the element being destroyed and recreated

#### Scenario: Title bound to the displayed route, not per-route markup
- **WHEN** a route becomes active
- **THEN** the header title SHALL be sourced from that route's configuration
- **AND** no route template SHALL author its own `<page-header>` element to supply the title
- **AND** no route SHALL change the header title while it is displayed
