# cube-css-modern-css-rules Specification

## Purpose

Enforces modern CSS best practices within the CUBE CSS methodology: logical viewport units (`vi` over `vw`), named containers (`container-name` required with `container-type`), and `color-mix()`/relative color syntax for derived color tokens.

## ADDED Requirements

### Requirement: `cube/prefer-vi-over-vw` recommends `vi` unit over `vw`
CSS values SHALL use the `vi` (viewport inline) unit instead of `vw` (viewport width) for logical consistency with writing-mode awareness.

#### Scenario: `vi` unit accepted
- **WHEN** a CSS file contains `font-size: clamp(1rem, 0.34vi + 0.91rem, 1.19rem);`
- **THEN** the rule SHALL not report an error

#### Scenario: `vw` unit rejected
- **WHEN** a CSS file contains `font-size: clamp(1rem, 0.34vw + 0.91rem, 1.19rem);`
- **THEN** the rule SHALL report an error: "Use 'vi' instead of 'vw' for logical viewport units"

#### Scenario: `vh` not affected
- **WHEN** a CSS file contains `block-size: 100vh;`
- **THEN** the rule SHALL not report an error (only `vw` → `vi` is enforced; `vh` → `vb` is a separate concern)

#### Scenario: `svw` and `lvw` also rejected
- **WHEN** a CSS file contains `inline-size: 100svw;` or `inline-size: 100lvw;`
- **THEN** the rule SHALL report an error recommending `svi` or `lvi` respectively

### Requirement: `cube/require-container-name` enforces naming containers
Elements that declare `container-type` SHALL also declare `container-name`.

#### Scenario: Both properties present accepted
- **WHEN** a CSS rule contains `container-type: inline-size; container-name: card;`
- **THEN** the rule SHALL not report an error

#### Scenario: `container` shorthand with name accepted
- **WHEN** a CSS rule contains `container: card / inline-size;`
- **THEN** the rule SHALL not report an error

#### Scenario: `container-type` without `container-name` rejected
- **WHEN** a CSS rule contains `container-type: inline-size;` but no `container-name` declaration
- **THEN** the rule SHALL report an error: "Elements with container-type must also declare container-name"

#### Scenario: `container-type: normal` ignored
- **WHEN** a CSS rule contains `container-type: normal;` (the default/reset value)
- **THEN** the rule SHALL not report an error

### Requirement: `cube/prefer-color-mix` recommends `color-mix()` for derived colors
When a custom property value in `@layer global` derives a color from another token (e.g., lighter/darker variants), `color-mix()` or relative color syntax SHALL be preferred over manual `oklch()` with hardcoded values.

#### Scenario: `color-mix()` accepted
- **WHEN** `@layer global` contains `--color-primary-hover: color-mix(in oklch, var(--color-primary) 80%, white);`
- **THEN** the rule SHALL not report an error

#### Scenario: Relative color syntax accepted
- **WHEN** `@layer global` contains `--color-primary-light: oklch(from var(--color-primary) calc(l + 0.2) c h);`
- **THEN** the rule SHALL not report an error

#### Scenario: Base color definition accepted
- **WHEN** `@layer global` contains `--color-primary: oklch(55% 0.25 260);`
- **THEN** the rule SHALL not report an error (this is a base definition, not a derivation)

#### Scenario: Derived color without `color-mix()` or relative syntax warned
- **WHEN** `@layer global` contains `--color-primary-light: oklch(75% 0.15 260);` and a `--color-primary` also exists
- **THEN** the rule SHALL report a warning: "Consider using color-mix() or relative color syntax to derive color variants from base tokens"
