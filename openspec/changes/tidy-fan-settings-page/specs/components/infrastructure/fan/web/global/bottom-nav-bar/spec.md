# Spec Delta

## MODIFIED Requirements

### Requirement: Centre slot and notch around the FAB

The navigation bar SHALL keep a centre slot between its second and third tabs on every route where it is shown, so that the four tabs stay at the same positions on every route. While the FAB is shown, the bar SHALL cut a notch around the FAB in its top edge at the centre slot, including while the FAB is sunk under a snack bar or a bottom banner (see FAB Menu), so that the sunk FAB reads as resting in its socket. While the FAB is not shown, the bar SHALL show no notch and the centre slot SHALL stay empty.

#### Scenario: Route with FAB actions
- **WHEN** the dashboard is displayed and the FAB is shown
- **THEN** the bar's top edge SHALL have a notch around the FAB at the centre slot

#### Scenario: Tickets shows the FAB
- **WHEN** the Tickets route is displayed
- **THEN** the FAB is shown with the Settings item (see FAB Menu)
- **AND** the bar's top edge SHALL have a notch around it

#### Scenario: Route without FAB actions
- **WHEN** the Settings route is displayed and the launcher has no item
- **THEN** the bar's top edge SHALL be straight, with no notch
- **AND** the centre slot SHALL be empty

#### Scenario: FAB sunk under a banner
- **WHEN** the dashboard is displayed with the FAB shown while the install banner is visible
- **THEN** the FAB SHALL rest sunk in the centre slot
- **AND** the bar's top edge SHALL keep the notch around it

#### Scenario: Tabs do not move between routes
- **WHEN** the user moves from the dashboard (FAB shown) to Settings (FAB hidden)
- **THEN** each of the four tabs SHALL stay at the same horizontal position
