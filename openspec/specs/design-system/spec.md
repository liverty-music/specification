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

---

### Requirement: SVG Icon Component
The system SHALL provide a centralized `<svg-icon>` custom element as the single source of truth for all SVG icon definitions, eliminating inline SVG duplication across templates.

#### Scenario: Icon rendering by name
- **WHEN** `<svg-icon name="home">` is rendered
- **THEN** the component SHALL display the SVG icon matching the given name
- **AND** only the matched icon SHALL be present in the DOM (via Aurelia `switch.bind`)
- **AND** unrecognized names SHALL render nothing (default-case fallback)

#### Scenario: Size variants
- **WHEN** `<svg-icon>` is rendered with a `size` attribute
- **THEN** the host element SHALL set `data-size` to the given value
- **AND** the component SHALL support sizes: xs (0.75rem), sm (1rem), md (1.25rem), lg (1.5rem), xl (2.5rem)
- **AND** the default size SHALL be md when no size is specified

#### Scenario: Icon set coverage
- **WHEN** the icon component is registered
- **THEN** it SHALL include at minimum these icons: home, search, discover, music, my-artists, ticket, tickets, settings, check, alert-triangle, warning, info, x-circle, x, chevron-right, arrow-left, trash, plus, map-pin, calendar, link, clock, globe, bell, lock, qr-code, list, grid

#### Scenario: Color inheritance
- **WHEN** `<svg-icon>` is placed inside a colored container
- **THEN** stroke-based icons SHALL use `stroke="currentColor"` to inherit the parent's text color
- **AND** fill-based icons (warning, x-circle) SHALL use `fill="currentColor"`

---

### Requirement: State Placeholder Component
The system SHALL provide a `<state-placeholder>` custom element for displaying empty, error, and informational states with a consistent centered layout.

#### Scenario: Empty state display
- **WHEN** `<state-placeholder icon="music" title="No artists" description="Start exploring">` is rendered
- **THEN** the component SHALL display an xl-sized svg-icon, a title heading, and a description paragraph
- **AND** the content SHALL be vertically and horizontally centered

#### Scenario: Conditional content rendering
- **WHEN** any of `icon`, `title`, or `description` props are empty
- **THEN** the corresponding element SHALL NOT be rendered (via `if.bind`)

#### Scenario: Custom content via slot
- **WHEN** child content is placed inside `<state-placeholder>`
- **THEN** the content SHALL be projected via `<au-slot>` below the description
- **AND** this SHALL allow pages to provide custom CTA buttons or links

---

### Requirement: Page Shell Component
The system SHALL provide a `<page-shell>` custom element that standardizes the page layout structure across route pages, eliminating duplicated page-layout and page-header CSS.

#### Scenario: Standard page layout
- **WHEN** `<page-shell title-key="nav.tickets">` wraps page content
- **THEN** the component SHALL render a `<main>` element with page-layout styles
- **AND** a `<header>` with an `<h1>` using the i18n key via `t.bind`
- **AND** default slot content SHALL appear below the header

#### Scenario: Header actions slot
- **WHEN** a page provides content to the `header-actions` named slot
- **THEN** the content SHALL appear in the header row beside the title
- **AND** this SHALL support buttons, toggles, or count badges

#### Scenario: Hidden header
- **WHEN** `<page-shell show-header.bind="false">` is used
- **THEN** the header SHALL NOT be rendered
- **AND** the page content SHALL fill the entire layout area

#### Scenario: Pages excluded from page-shell
- **WHEN** a route page requires custom attributes on its `<main>` element (e.g., `data-search-mode.bind`)
- **THEN** that page SHALL NOT use `<page-shell>` and SHALL manage its own layout structure
