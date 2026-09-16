## Purpose

Defines how any data-fetching route coordinates Aurelia's two lifecycles — the
navigation-scoped route lifecycle and the DOM-scoped component lifecycle — so
that a route paints something meaningful immediately, never blocks navigation on
data, and returns the fan to where they were. The contract is app-wide so each
route inherits the behavior instead of re-deriving it.

## ADDED Requirements

### Requirement: Render state is reflected after the route's first render

A route SHALL NOT assign render-bound state during a pre-activation route
lifecycle hook, including when the content is served from a cache. Doing so
places the full content inside the component's first render, so no intermediate
frame can be painted. Reflecting fetched or cached content SHALL happen on the
component lifecycle, after the component's first render has been produced.

#### Scenario: Cached content is not folded into the first render

- **WHEN** a route can serve its content from a cache on re-entry
- **THEN** the component's first render SHALL contain only the route's
  data-independent presentation
- **AND** the cached content SHALL be reflected afterwards, from the component
  lifecycle

#### Scenario: Freshly fetched content is reflected the same way

- **WHEN** a route's fetch resolves after the view has attached
- **THEN** the arriving content SHALL be reflected through the same path as
  cached content, so both produce the same sequence of renders

### Requirement: An expensive render is preceded by a frame paint

When a route's content render is expensive enough to be perceived, the route
SHALL yield a paint after its data-independent frame is renderable and before the
expensive content is rendered, so the fan sees the frame first. The yield SHALL
be one the browser can paint across; a continuation that resolves on the
microtask queue SHALL NOT be relied upon, because microtasks drain before the
browser's next paint. Where a route plays an entrance animation, that animation
MAY serve as the yield.

#### Scenario: The frame is visible before the content

- **WHEN** a fan navigates to a route whose content render is expensive
- **THEN** at least one painted frame SHALL show the route's data-independent
  presentation without its content
- **AND** that frame SHALL precede the frame containing the content

#### Scenario: Suppressing animation does not remove the yield

- **WHEN** a route's entrance animation is suppressed, including for a fan who
  prefers reduced motion
- **THEN** the route SHALL still yield a paint before its expensive content
  renders, by a means other than the animation

### Requirement: Long lists render only what is in view

A route presenting a list that can exceed the viewport SHALL limit style, layout
and paint work to the portion the fan can see, and SHALL render the remainder as
it is scrolled into view. The list's scroll extent SHALL remain stable enough
that scrolling does not jump.

#### Scenario: Off-screen list content is not rendered

- **WHEN** a route renders a list longer than the viewport
- **THEN** the portion outside the viewport SHALL NOT incur style, layout or
  paint work
- **AND** scrolling toward it SHALL render it in time to be seen

### Requirement: Scroll position survives navigation away and back

A route presenting a scrollable list SHALL restore the scroll position the fan
left it at when they navigate away and return within the session. Restoration
SHALL be applied once the route's content is reflected, and SHALL be clamped to
the restored content's extent when that content is shorter than the saved
position.

#### Scenario: Returning to a tab restores the scroll position

- **WHEN** a fan scrolls into a route's list, navigates to another tab, and
  returns
- **THEN** the list SHALL be restored at the position it had when they left

#### Scenario: Shorter content clamps instead of failing

- **WHEN** the restored content is shorter than the saved scroll position
- **THEN** the view SHALL clamp to the end of the content
- **AND** SHALL NOT error or reset to the top

### Requirement: The rendering contract is provided, not re-implemented

The behaviors in this capability SHALL be provided by shared, centrally
registered mechanism rather than implemented separately by each route. A route
SHALL obtain them by declaring what data it needs and what its scrollable region
is; satisfying the contract SHALL NOT require a route to write its own
navigation-lifecycle wiring. Behavior that must run earlier than any
per-component route hook — such as the optimistic page-identity switch at
navigation intent — is out of this mechanism's scope and SHALL remain where it
can fire at navigation intent.

#### Scenario: A new data-fetching route inherits the behavior

- **WHEN** a new data-fetching route is added and declares its data and
  scrollable region
- **THEN** it SHALL start its fetch non-blocking, reflect content after first
  render, and save and restore scroll position
- **AND** it SHALL NOT need to implement navigation-lifecycle hooks to do so

#### Scenario: Shared mechanism is scoped to routes

- **WHEN** the shared mechanism is registered application-wide
- **THEN** it SHALL apply to routed components only
- **AND** SHALL NOT alter the lifecycle of every custom element in the
  application
