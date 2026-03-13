# Design System

## Purpose

Defines the centralized design token system and visual foundation for the Liverty Music application, ensuring consistency across all screens through plain CSS custom properties in `tokens.css`, a dark-first theme, and optimized display font loading.

## Requirements

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

### Requirement: Dark Theme as Default
The system SHALL apply a dark-first visual theme consistently across all screens and components.

#### Scenario: Dark background applied globally
- **WHEN** any screen is rendered
- **THEN** the body background SHALL use a dark gradient or solid dark color from the surface token palette
- **AND** primary text SHALL be white or light gray (meeting WCAG AA contrast ratio against the dark background)

#### Scenario: Dark theme consistency across onboarding
- **WHEN** the user navigates from Landing Page -> Artist Discovery -> Loading -> Dashboard
- **THEN** all screens SHALL use the same dark surface palette
- **AND** there SHALL be no jarring light-to-dark or dark-to-light transitions between screens

---

### Requirement: Display Font Loading
The system SHALL load and apply a display font for headings with appropriate fallback and performance optimization.

#### Scenario: Font preloading
- **WHEN** the application loads
- **THEN** the system SHALL preconnect to the font provider domains (fonts.googleapis.com and fonts.gstatic.com) in the HTML head
- **AND** the preconnect to `fonts.gstatic.com` SHALL include the `crossorigin` attribute
- **AND** the system SHALL load the display font with `font-display: swap` and include necessary weights (e.g., Bold 700, Extra-Bold 800) to prevent layout shifts or faux-bolding during load
- **AND** the system SHALL use `system-ui` as the immediate fallback until the display font is ready

---

### Requirement: View Transitions as route animation system
The design system SHALL provide View Transition styles as the primary route animation mechanism, replacing CSS keyframe animations on `au-viewport > *`.

#### Scenario: View transition styles defined
- **WHEN** the design system CSS is loaded
- **THEN** the global stylesheet SHALL define `::view-transition-old(root)` and `::view-transition-new(root)` pseudo-element styles
- **AND** the transition duration and easing SHALL use the design system tokens (`--transition-route-duration`, `--transition-route-easing`)

#### Scenario: Keyframe fallback preserved
- **WHEN** the browser does not support View Transitions
- **THEN** the existing `@keyframes page-enter` animation on `au-viewport > *` SHALL remain as a fallback
- **AND** the fallback SHALL be gated behind `@supports not (view-transition-name: x)`

---

### Requirement: Container Query infrastructure
The design system SHALL provide base styles for declaring container contexts.

#### Scenario: Container type with named container
- **WHEN** a component needs to use Container Queries for responsive child layout
- **THEN** the component's wrapper element SHALL declare `container-type: inline-size` with a corresponding `container-name`
- **AND** child elements SHALL use `@container <name>` rules referencing the design system breakpoint tokens
- **AND** the `cube/require-container-name` stylelint rule SHALL report zero warnings
