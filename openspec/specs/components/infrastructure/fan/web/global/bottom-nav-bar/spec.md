# Bottom Nav Bar

## Purpose

Provides the primary bottom tab navigation for moving between the app's main routes, showing an animated selection state and switching the visible route immediately on tap without waiting for its data to load, hiding on fullscreen routes.

## Requirements

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

### Requirement: App shell hides navigation on fullscreen routes
The app shell's navigation-visibility state SHALL be `false` for fullscreen routes and `true` for other routes.

#### Scenario: Fullscreen route
- **WHEN** the active route path is `welcome`, `onboarding/discover`, or `auth/callback`
- **THEN** the navigation SHALL be hidden

#### Scenario: Non-fullscreen route
- **WHEN** the active route path is `dashboard` or `about`
- **THEN** the navigation SHALL be shown

### Requirement: Animated selection state

Selection controls (bottom-nav tabs, filter chips) SHALL animate into the selected state driven by a real
selection attribute (not hover), with a reduced-motion fallback. A shape morph SHALL be used only where it
reads as intentional: the bottom-nav tab morphs rounder with a spatial spring. Pill-shaped filter chips SHALL
NOT shape-morph — their corner roundness already saturates, so a radius tween is visually inert/janky;
instead a chip signals selection with color + a persistent selected state layer.

#### Scenario: Selecting a nav tab springs into state

- **WHEN** a user selects a navigation tab
- **THEN** the selected tab animates into its selected treatment — color plus a spatial-spring shape morph
  (rounder) — rather than switching statically

#### Scenario: Selecting a filter chip is clearly signalled without a shape morph

- **WHEN** a user selects a filter chip
- **THEN** the chip takes its selected treatment via color + a persistent selected state layer (the pill shape
  is unchanged), avoiding an inert radius tween

#### Scenario: Selection is driven by state, not hover

- **WHEN** the selected treatment is evaluated
- **THEN** it reflects the actual selected/`aria`-state attribute and does not trigger on hover alone

### Requirement: Menu-tab navigation attaches the view before data resolves
Every bottom-nav menu-tab route SHALL NOT block the router view swap on its data fetch. The route's `loading()` hook SHALL complete without awaiting network/RPC work, so the incoming view attaches immediately and the outgoing view is never held frozen waiting for data. This applies to every route reachable from the bottom nav, not to an enumerated subset: adding a tab brings that route under this requirement. A `loading()` hook SHALL also not assign render-bound state synchronously from a cache, because that places the full render inside the component's first render exactly as an `await` places it ahead of the view swap; reflecting render state belongs to the component lifecycle. A route MAY deliberately block navigation on data when showing the incoming view in an intermediate state would be wrong (for example, parking an unverified fan before a payment step); such a case SHALL be documented as an exception at the call site.

#### Scenario: Tapping a menu tab swaps the view immediately
- **WHEN** the user taps a bottom-nav menu tab whose route fetches data
- **THEN** the router SHALL attach the new route's view without waiting for the fetch to resolve
- **AND** the previous screen SHALL NOT remain displayed while the fetch is in flight

#### Scenario: Data fetch is kicked off non-blocking from loading()
- **WHEN** a menu-tab route's `loading()` hook runs
- **THEN** the data fetch SHALL be started as fire-and-forget (not awaited inside `loading()`)
- **AND** `loading()` SHALL resolve as soon as its synchronous prelude completes

#### Scenario: A cached result does not collapse into the first render
- **WHEN** a menu-tab route can serve its content from a cache on re-entry
- **THEN** `loading()` SHALL NOT assign that cached content to render-bound state
- **AND** the cached content SHALL be reflected from the component lifecycle, so the first render shows the route's loading presentation rather than the full content

#### Scenario: A newly added bottom-nav tab is covered
- **WHEN** a route is added to the bottom navigation
- **THEN** that route SHALL satisfy this requirement from the moment it appears in the nav
- **AND** no enumeration of route names SHALL be required to bring it into scope

### Requirement: In-flight state is shown via the route's existing UI
While a menu-tab route's data is loading, the attached view SHALL present that route's existing loading indicator (spinner/skeleton) or empty state, and SHALL surface an error state if the fetch fails. This SHALL hold on re-entry as well as on first load: a route serving cached content SHALL present its loading indicator for as long as the content is not yet reflected, and SHALL NOT present an empty state during that window.

#### Scenario: Spinner shown immediately after attach
- **WHEN** a menu-tab route attaches with its fetch still in flight
- **THEN** the view SHALL render with `isLoading` true so the spinner/skeleton is visible from first paint
- **AND** the populated content SHALL replace it once the fetch resolves

#### Scenario: Fetch failure shows an error/empty state, not a frozen screen
- **WHEN** a menu-tab route's non-blocking fetch rejects with a non-abort error
- **THEN** the view SHALL display the route's error or empty state
- **AND** navigation SHALL NOT have been blocked by the failure

#### Scenario: Re-entry shows the loading presentation, never an empty flash
- **WHEN** a menu-tab route re-enters with cached content not yet reflected
- **THEN** the view SHALL show that route's loading presentation
- **AND** the route's empty state SHALL NOT be rendered at any point before the load has settled

### Requirement: Late-arriving data renders regardless of attach order
A menu-tab route's rendering SHALL be order-independent: whether the fetched data resolves before or after the view attaches, the resulting content (including canvas-seeded UI such as the Discovery bubbles) SHALL render correctly.

#### Scenario: Data resolves before the view attaches
- **WHEN** a non-blocking fetch resolves before the route's view finishes attaching
- **THEN** the attaching view SHALL pick up the already-present data and render it

#### Scenario: Data resolves after the view attaches
- **WHEN** a non-blocking fetch resolves after the route's view has attached
- **THEN** the observed data change SHALL update the rendered content (e.g. the canvas seeds artists once its context exists)
