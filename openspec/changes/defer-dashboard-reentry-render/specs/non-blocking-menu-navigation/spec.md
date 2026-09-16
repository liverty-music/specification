## MODIFIED Requirements

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
