## ADDED Requirements

### Requirement: Primary role takes a white label at every size

The `primary` colour role SHALL keep brand-primary's hue and chroma at a lightness where its paired `on-primary` role, white, measures at least 4.5:1, so that text on a primary fill passes at every size and does not depend on WCAG's large-text minimum. The brand colour itself (`--color-brand-primary`) SHALL stay unchanged for surfaces that carry no text on it: the FAB's gradient, brand lines and glows.

#### Scenario: Primary role takes a white label at every size
- **WHEN** white `on-primary` text of any size is placed on the `primary` fill
- **THEN** the pair SHALL measure at least 4.5:1
- **AND** the `primary` fill SHALL have brand-primary's hue and chroma

#### Scenario: The brand colour stays for surfaces without text
- **WHEN** the FAB, a brand-gradient line or a brand glow is rendered
- **THEN** it SHALL use the brand colour, not the darker `primary` role
