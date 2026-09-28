## ADDED Requirements

### Requirement: Menu-tab navigation never waits on data
Every bottom-nav menu-tab route SHALL NOT block the router view swap on its data fetch. The route's `loading()` hook SHALL complete without awaiting network/RPC work, so the incoming view attaches immediately and the outgoing view is never held frozen waiting for data. This applies to every route reachable from the bottom nav, not to an enumerated subset: adding a tab brings that route under this requirement. A `loading()` hook SHALL also not assign render-bound state from a cache; reflecting render state belongs to the component lifecycle. A route MAY reflect cached content before its first render when the render it causes is bounded by what the fan can see, so that re-entry shows the content in its first paint instead of a loading placeholder followed by the content. A route MAY deliberately block navigation on data when showing the incoming view in an intermediate state would be wrong (for example, parking an unverified fan before a payment step); such a case SHALL be documented as an exception at the call site.

#### Scenario: Tapping a menu tab swaps the view immediately
- **WHEN** the user taps a bottom-nav menu tab whose route fetches data
- **THEN** the router SHALL attach the new route's view without waiting for the fetch to resolve
- **AND** the previous screen SHALL NOT remain displayed while the fetch is in flight

#### Scenario: Data fetch is kicked off non-blocking from loading()
- **WHEN** a menu-tab route's `loading()` hook runs
- **THEN** the data fetch SHALL be started as fire-and-forget (not awaited inside `loading()`)
- **AND** `loading()` SHALL resolve as soon as its synchronous prelude completes

#### Scenario: A cached result is reflected from the component lifecycle
- **WHEN** a menu-tab route can serve its content from a cache on re-entry
- **THEN** `loading()` SHALL NOT assign that cached content to render-bound state
- **AND** the cached content SHALL be reflected from the component lifecycle
- **AND** where it is reflected before the first render, the render it causes SHALL be bounded by what the fan can see

#### Scenario: A newly added bottom-nav tab is covered
- **WHEN** a route is added to the bottom navigation
- **THEN** that route SHALL satisfy this requirement from the moment it appears in the nav
- **AND** no enumeration of route names SHALL be required to bring it into scope

## REMOVED Requirements

### Requirement: Menu-tab navigation attaches the view before data resolves
**Reason**: It required cached content to be kept out of the first render. That was a workaround for an unbounded render, and it made re-entry paint a loading placeholder and then the content. With the render bounded, the cached content can be in the first paint.
**Migration**: Replaced by "Menu-tab navigation never waits on data", which keeps every rule except that one, and still forbids assigning render state in `loading()`.
