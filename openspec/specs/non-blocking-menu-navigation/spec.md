# non-blocking-menu-navigation Specification

## Purpose

Keeps every route reachable from the bottom navigation swapping into view the
moment a fan taps its tab, rather than holding the screen they are leaving until
data arrives. Fetching stays the route's job; what this capability fixes is where
that work sits relative to the view swap, and what the fan sees while it runs.

## Requirements
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

### Requirement: Navigating away cancels the in-flight fetch
Because the fetch outlives `loading()`, a menu-tab route SHALL abort its in-flight request when the route is deactivated, and an `AbortError` SHALL be treated as a non-error.

#### Scenario: Leaving the tab aborts the request
- **WHEN** the user navigates away from a menu-tab route before its fetch resolves
- **THEN** the route's deactivation hook SHALL abort the request's `AbortController`
- **AND** the resulting `AbortError` SHALL NOT be logged as an error or shown to the user

### Requirement: Data-ready side effects gate on observed data arrival
Side effects that must only run once a route's data is genuinely present (e.g. the Dashboard post-signup/guest celebration and the onboarding-completion latch) SHALL be triggered by observing the arrival of that data via Aurelia reactivity (`@watch`/`@observable`), NOT by relying on the router having awaited the fetch before `attached()`.

#### Scenario: Celebration fires only once the timetable is real
- **WHEN** the Dashboard loads data non-blocking and the data arrives after the view has attached
- **THEN** the celebration decision SHALL be evaluated when the loaded data is observed to be present
- **AND** the celebration SHALL NOT be presented over a still-loading (spinner) timetable

#### Scenario: Completion latch waits for engagement data
- **WHEN** the onboarding-completion latch condition depends on loaded follow/engagement data
- **THEN** the latch SHALL be evaluated upon observed arrival of that data
- **AND** it SHALL NOT short-circuit on not-yet-loaded state when the route attaches

### Requirement: Late-arriving data renders regardless of attach order
A menu-tab route's rendering SHALL be order-independent: whether the fetched data resolves before or after the view attaches, the resulting content (including canvas-seeded UI such as the Discovery bubbles) SHALL render correctly.

#### Scenario: Data resolves before the view attaches
- **WHEN** a non-blocking fetch resolves before the route's view finishes attaching
- **THEN** the attaching view SHALL pick up the already-present data and render it

#### Scenario: Data resolves after the view attaches
- **WHEN** a non-blocking fetch resolves after the route's view has attached
- **THEN** the observed data change SHALL update the rendered content (e.g. the canvas seeds artists once its context exists)
