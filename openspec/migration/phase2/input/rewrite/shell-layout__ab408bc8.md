<!-- spec: shell-layout | target: components/infrastructure/fan/web/route/dashboard | flags: HISTORIC | new_name: Dashboard handles event selection directly -->

### Requirement: live-highway component eliminated
The `live-highway` custom element SHALL be removed and its responsibilities inlined into `dashboard-route`.

#### Scenario: Event selection handled by dashboard
- **WHEN** a user taps an event card in the concert list
- **THEN** `dashboard-route` SHALL handle the `event-selected` custom event and open the `event-detail-sheet` dialog
- **AND** there SHALL be no `live-highway` custom element in the DOM tree

#### Scenario: Loading and empty states managed by promise.bind
- **WHEN** concert data is loading or empty
- **THEN** the dashboard's `promise.bind` directive SHALL manage pending/then/catch states directly
- **AND** there SHALL be no duplicate loading/empty state management
