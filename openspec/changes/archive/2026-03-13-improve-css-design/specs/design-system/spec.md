## MODIFIED Requirements

### Requirement: Design Token Definition
The system SHALL define a centralized set of design tokens using plain CSS custom properties in `src/styles/tokens.css` to ensure visual consistency across all screens.

#### Scenario: Color tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define the following color token groups via CSS custom properties in `tokens.css`:
  - `--color-brand-primary`: oklch(58.5% 0.233 277deg)
  - `--color-brand-secondary`: oklch(54.1% 0.281 293deg)
  - `--color-brand-accent`: oklch(78.9% 0.154 211deg)
  - `--color-surface-base`: oklch(14.5% 0.014 286deg)
  - `--color-surface-raised`: oklch(17.8% 0.014 286deg)
  - `--color-surface-overlay`: oklch(21% 0.014 286deg)
  - `--color-text-primary`: oklch(98.5% 0 0deg)
  - `--color-text-secondary`: oklch(78.8% 0.013 286deg)
  - `--color-text-muted`: oklch(55.6% 0.014 286deg)
- **AND** all components SHALL reference these tokens instead of hardcoded color values
- **AND** tokens SHALL be defined on `:root` using standard CSS custom property syntax, not Tailwind's `@theme` directive

#### Scenario: Typography tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define font family tokens:
  - `--font-display`: "Outfit", system-ui, sans-serif for hero copy, card headlines, section titles
  - `--font-body`: system-ui, -apple-system, sans-serif for paragraphs, labels, metadata
- **AND** the system SHALL define a type scale with sizes for mega (4xl or larger), heading (2xl-3xl), body (base-lg), caption (xs-sm)

#### Scenario: Shape tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define radius tokens: `--radius-card` (1rem), `--radius-button` (0.75rem), `--radius-sheet` (1.5rem)
- **AND** the system SHALL define shadow tokens: `--shadow-card-glow`, `--shadow-sheet`, `--shadow-button`

#### Scenario: Spacing scale tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define a fluid spacing scale using `clamp()` with tokens from `--space-3xs` through `--space-3xl`
- **AND** composition primitives and block styles SHALL reference these spacing tokens instead of fixed pixel values

#### Scenario: Container query breakpoint tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define container query breakpoint tokens for component-level responsive design:
  - `--container-sm`: 320px
  - `--container-md`: 480px
  - `--container-lg`: 640px
- **AND** components using Container Queries SHALL reference these tokens for consistent breakpoints

#### Scenario: View transition tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define view transition duration and easing tokens:
  - `--transition-route-duration`: 200ms
  - `--transition-route-easing`: ease-out
- **AND** route transitions SHALL reference these tokens instead of hardcoded values

---

### Requirement: Container Query infrastructure
The design system SHALL provide base styles for declaring container contexts.

#### Scenario: Container type with named container
- **WHEN** a component needs to use Container Queries for responsive child layout
- **THEN** the component's wrapper element SHALL declare `container-type: inline-size` with a corresponding `container-name`
- **AND** child elements SHALL use `@container <name>` rules referencing the design system breakpoint tokens
- **AND** the `cube/require-container-name` stylelint rule SHALL report zero warnings
