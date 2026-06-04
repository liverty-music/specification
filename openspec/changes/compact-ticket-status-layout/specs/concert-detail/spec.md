## ADDED Requirements

### Requirement: Compact journey-status control layout

The concert detail sheet's ticket-journey status control SHALL render in a compact layout whose outcome phase is arranged horizontally in a single row, so the control's vertical footprint is roughly half of a vertically stacked outcome layout. The control SHALL preserve every journey status node, the radiogroup semantics, keyboard navigation, and the canonical per-status label, icon, and hue.

#### Scenario: Outcome routes arranged horizontally

- **WHEN** the ticket-journey status control is displayed
- **THEN** the win route nodes (`unpaid`, `paid`) and the lose route node (`lost`) SHALL be arranged horizontally in a single row rather than as vertically stacked bordered cards
- **AND** the win-route nodes SHALL be connected by the horizontal `›` flow connector (not a vertical `↓` connector)
- **AND** the win route and lose route SHALL remain visually distinguishable via a separator and their per-status hues

#### Scenario: All status nodes and behavior preserved

- **WHEN** the compact layout is rendered
- **THEN** all five status nodes (`tracking`, `applied`, `unpaid`, `paid`, `lost`) SHALL still be present and selectable
- **AND** each node SHALL retain a tap target of at least 44px
- **AND** the radiogroup role, keyboard navigation, and `data-testid` hooks SHALL be unchanged
- **AND** each node's label, icon, and hue SHALL still be sourced from the canonical journey-status presentation map

#### Scenario: Flow connector is not cramped

- **WHEN** a flow connector (`›`) is rendered between two status nodes in either the process phase or the outcome phase
- **THEN** the connector SHALL have dedicated inline spacing on both sides independent of the container gap
- **AND** the connector glyph SHALL be rendered at a size that is legible rather than hairline

#### Scenario: Narrow viewport does not overflow

- **WHEN** the control is displayed on a narrow mobile viewport where the outcome row cannot fit on one line
- **THEN** the outcome row SHALL wrap rather than overflow horizontally
- **AND** the control's vertical footprint SHALL remain smaller than the prior vertically stacked outcome layout
