<!-- spec: bubble-state-management | target: components/infrastructure/fan/web/route/discovery | flags: CLASSNAME | new_name: Bubble canvas reads deferred until element is visible -->

### Requirement: Bubble canvas reads deferred until element is visible
The system SHALL NOT read canvas dimensions while the canvas element has `display: none` or zero-size layout.

#### Scenario: Canvas rect read when visible
- **WHEN** the system needs canvas dimensions and the canvas element is visible
- **THEN** the system SHALL return accurate width and height values

#### Scenario: Canvas rect read when hidden
- **WHEN** the system needs canvas dimensions and the canvas element is hidden (e.g., during search mode)
- **THEN** the system SHALL defer the read until the element becomes visible (via `requestAnimationFrame`)
- **AND** SHALL NOT spawn bubbles at position (0, 0)
