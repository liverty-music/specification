# Design System

## Purpose

Defines the centralized design token system and visual foundation for the Liverty Music application, ensuring consistency across all screens through Tailwind CSS v4 design tokens, a dark-first theme, and optimized display font loading.

## Requirements

### Requirement: Design Token Definition
The system SHALL define a centralized set of design tokens using Tailwind CSS v4's `@theme` directive to ensure visual consistency across all screens.

#### Scenario: Color tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define the following color token groups via CSS custom properties:
  - `--color-brand-primary`: indigo-500
  - `--color-brand-secondary`: violet-500
  - `--color-brand-accent`: cyan-400
  - `--color-surface-background`: gray-950
  - `--color-surface-layer-1`: gray-900
  - `--color-surface-layer-2`: gray-800
  - `--color-text-primary`: white
  - `--color-text-secondary`: gray-300
  - `--color-text-muted`: gray-500
- **AND** all components SHALL reference these tokens instead of hardcoded color values

#### Scenario: Typography tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define font family tokens:
  - `--font-display`: display/heading font (e.g., Outfit) for hero copy, card headlines, section titles
  - `--font-body`: body text font (system-ui, sans-serif) for paragraphs, labels, metadata
- **AND** the system SHALL define a type scale with sizes for mega (4xl+), heading (2xl-3xl), body (base-lg), caption (xs-sm)

#### Scenario: Spacing and shape tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define radius tokens: `--radius-card` (1rem), `--radius-button` (0.75rem), `--radius-sheet` (1.5rem)
- **AND** the system SHALL define shadow tokens: `--shadow-card-glow`, `--shadow-sheet`, `--shadow-button`

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
- **AND** the system SHALL load the display font with `font-display: swap` to prevent invisible text during load
- **AND** the system SHALL use `system-ui` as the immediate fallback until the display font is ready
