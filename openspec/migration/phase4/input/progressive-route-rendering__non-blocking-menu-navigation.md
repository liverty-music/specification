<!-- change: progressive-route-rendering | old_cap: non-blocking-menu-navigation -->
### Requirement: Conformance is structural, not per-route discipline

A bottom-nav menu-tab route SHALL satisfy the non-blocking contract by declaring
the data it needs, leaving the shared route-rendering mechanism to start that
fetch non-blocking and to cancel it on deactivation. A route SHALL NOT be
required to implement its own `loading()` wiring in order to conform, so the
contract cannot be missed by a route that simply forgets it. A route that must
deliberately block navigation on data SHALL declare that intent explicitly, and
SHALL be recorded as a documented exception.

#### Scenario: A route conforms without writing lifecycle wiring

- **WHEN** a menu-tab route declares its data requirement
- **THEN** its fetch SHALL be started non-blocking on navigation and cancelled
  when the route is deactivated
- **AND** the route SHALL NOT implement a navigation lifecycle hook to achieve
  this

#### Scenario: Deliberate blocking is declared, not implicit

- **WHEN** a route must hold navigation until its data resolves
- **THEN** that intent SHALL be expressed explicitly
- **AND** it SHALL be recorded as an exception rather than appearing as an
  ordinary implementation detail

