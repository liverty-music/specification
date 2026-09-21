<!-- spec: shell-layout | target: components/infrastructure/fan/web/route/dashboard | flags: HISTORIC | new_name: Dashboard handles event selection directly -->

### Requirement: Dashboard handles event selection directly

`dashboard-route` SHALL handle event selection and loading/empty states directly.

#### Scenario: Event selection handled by dashboard
- **WHEN** a user taps an event card in the concert list
- **THEN** `dashboard-route` SHALL handle the `event-selected` custom event and open the `event-detail-sheet` dialog

#### Scenario: Loading and empty states managed by promise.bind
- **WHEN** concert data is loading or empty
- **THEN** the dashboard's `promise.bind` directive SHALL manage pending/then/catch states directly
