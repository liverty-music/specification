## ADDED Requirements

### Requirement: Single source of design tokens

The system SHALL define its design tokens (color, spacing, typographic scale,
radius, elevation, and motion) in **one shared source** consumed by all three
web audiences. Each token value SHALL be defined once; audiences SHALL NOT keep
divergent copies of the same token, and SHALL NOT redefine a token under a
different name for the same role.

#### Scenario: Same primitive renders consistently across audiences

- **WHEN** the same UI primitive is rendered in fan-web, the admin console, and the organizer console
- **THEN** it uses identical token values (same brand color, spacing, radius, and type scale) so it looks the same in every audience

#### Scenario: A token change propagates everywhere from one edit

- **WHEN** a shared token's value is changed in the single source
- **THEN** the new value is reflected across all three audiences without any per-audience token edit
