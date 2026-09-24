<!-- spec: frontend-testing | target: components/infrastructure/fan/web/global/live-highway | flags: CLASSNAME | new_name: Live highway displays grouped events -->
<!-- implementation names to remove: detailSheet -->

### Requirement: Live highway displays grouped events
The `LiveHighway` component SHALL render date groups and delegate event selection.

#### Scenario: Empty state
- **WHEN** `dateGroups` is an empty array
- **THEN** `isEmpty` SHALL return `true`

#### Scenario: Event selection delegation
- **WHEN** `onEventSelected` is called with a custom event containing a `LiveEvent`
- **THEN** it SHALL call `detailSheet.open` with that event
