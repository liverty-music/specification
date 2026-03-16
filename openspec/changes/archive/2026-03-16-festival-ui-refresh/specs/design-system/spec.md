## MODIFIED Requirements

### Requirement: Design Token Definition
The system SHALL define a centralized set of design tokens using plain CSS custom properties in `src/styles/tokens.css` to ensure visual consistency across all screens.

#### Scenario: Color tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define the following color token groups via CSS custom properties in `tokens.css`:
  - `--color-brand-primary`: oklch(65% 0.28 350deg) (hot pink)
  - `--color-brand-secondary`: oklch(62% 0.25 255deg) (electric blue)
  - `--color-brand-accent`: oklch(82% 0.22 140deg) (lime green)
  - `--color-surface-base`: oklch(18% 0.04 275deg) (deep navy)
  - `--color-surface-raised`: oklch(22% 0.04 275deg)
  - `--color-surface-overlay`: oklch(26% 0.04 275deg)
  - `--color-text-primary`: oklch(98.5% 0 0deg)
  - `--color-text-secondary`: oklch(82% 0.02 275deg) (warm-tinted light gray)
  - `--color-text-muted`: oklch(60% 0.03 275deg) (warm-tinted dim gray)
- **AND** all components SHALL reference these tokens instead of hardcoded color values
- **AND** tokens SHALL be defined on `:root` using standard CSS custom property syntax, not Tailwind's `@theme` directive

#### Scenario: Stage color tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define per-stage identity color tokens:
  - `--color-stage-home`: oklch(72% 0.2 55deg) (orange)
  - `--color-stage-near`: oklch(75% 0.18 195deg) (cyan)
  - `--color-stage-away`: oklch(68% 0.25 330deg) (magenta)
- **AND** components needing stage-aware styling SHALL reference these tokens
- **AND** stage colors SHALL be applied via `data-stage` attribute selectors in the block layer (CUBE CSS exception pattern), not in the composition layer

#### Scenario: Typography tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define font family tokens:
  - `--font-display`: "Righteous", "Outfit", system-ui, sans-serif for hero copy, card headlines, section titles
  - `--font-body`: "Poppins", system-ui, -apple-system, sans-serif for paragraphs, labels, metadata
- **AND** the system SHALL define a type scale with sizes for mega (4xl or larger), heading (2xl-3xl), body (base-lg), caption (xs-sm)

#### Scenario: Righteous font-weight constraint
- **WHEN** `--font-display` resolves to Righteous
- **THEN** components SHALL use `font-weight: normal` (400) or omit weight entirely for Righteous-rendered text
- **AND** components SHALL NOT specify `font-weight: 700` or higher when using `--font-display`, as Righteous provides only weight 400 and higher values trigger faux-bold rendering

#### Scenario: Border color tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define border color tokens:
  - `--color-border-subtle`: oklch(98.5% 0 0deg / 12%)
  - `--color-border-muted`: oklch(98.5% 0 0deg / 22%)

#### Scenario: Shadow tokens reference brand color via relative color syntax
- **WHEN** the design system is initialized
- **THEN** the system SHALL define shadow tokens using relative color syntax referencing `--color-brand-primary`:
  - `--shadow-card-glow`: 0 4px 24px -4px oklch(from var(--color-brand-primary) l c h / 20%)
  - `--shadow-button`: 0 4px 16px -2px oklch(from var(--color-brand-primary) l c h / 30%)
- **AND** the `--shadow-sheet` and `--shadow-soft` tokens SHALL remain unchanged
- **AND** shadow tokens SHALL NOT contain hardcoded oklch values; they SHALL always derive from brand color tokens

#### Scenario: Shape tokens defined
- **WHEN** the design system is initialized
- **THEN** the system SHALL define radius tokens: `--radius-card` (1rem), `--radius-button` (0.75rem), `--radius-sheet` (1.5rem)

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

### Requirement: Display Font Loading
The system SHALL load and apply display and body fonts with appropriate fallback and performance optimization.

#### Scenario: Font preloading
- **WHEN** the application loads
- **THEN** the system SHALL preconnect to the font provider domains (fonts.googleapis.com and fonts.gstatic.com) in the HTML head
- **AND** the preconnect to `fonts.gstatic.com` SHALL include the `crossorigin` attribute
- **AND** the system SHALL load Righteous (weight 400) and Poppins (weights 300, 400, 500, 600, 700) with `font-display: swap`
- **AND** the existing Outfit font `<link>` SHALL be retained as a fallback for `--font-display`
- **AND** the system SHALL use Outfit as the second fallback for `--font-display` and system-ui as the fallback for `--font-body`

## ADDED Requirements

### Requirement: Stage-Colored Header Block
The dashboard stage header SHALL apply per-stage identity colors via `data-stage` attribute selectors within the block layer (`@scope (dashboard-route)`), following the CUBE CSS exception pattern.

#### Scenario: Stage header color via data-stage exception
- **WHEN** a stage header span has `data-stage="home"`
- **THEN** the background SHALL use `--color-stage-home`
- **WHEN** a stage header span has `data-stage="near"`
- **THEN** the background SHALL use `--color-stage-near`
- **WHEN** a stage header span has `data-stage="away"`
- **THEN** the background SHALL use `--color-stage-away`
- **AND** text color SHALL be `--color-surface-base` (dark on vibrant background) for contrast

#### Scenario: Stage header typography
- **WHEN** stage header text is rendered
- **THEN** the text SHALL use `--font-display` with `font-weight: normal` (400, matching Righteous single weight)
- **AND** the text SHALL be uppercase with centered alignment

#### Scenario: WCAG contrast on stage headers
- **WHEN** stage header text is rendered
- **THEN** the text-to-background contrast ratio SHALL meet WCAG AA (4.5:1 for normal text, 3:1 for large text)

### Requirement: Nav Glow Block Styling
The bottom navigation bar SHALL apply glow and gradient effects within its own block layer (`@scope (bottom-nav-bar)`), not in the composition layer.

#### Scenario: Active nav tab glow
- **WHEN** a navigation tab is in active state (`data-active="true"`)
- **THEN** the tab SHALL display a subtle box-shadow glow using `--color-brand-accent` at reduced opacity
- **AND** the glow SHALL transition smoothly using `--transition-normal`

#### Scenario: Nav top border gradient via pseudo-element
- **WHEN** the bottom navigation bar is rendered
- **THEN** the top border area SHALL display a gradient from `--color-brand-primary` through `--color-brand-secondary` to `--color-brand-accent`
- **AND** the gradient SHALL be implemented via a `::before` pseudo-element with `background-image: linear-gradient(...)` and `block-size: 1px`
- **AND** the implementation SHALL NOT use `border-image` (which disables `border-radius`)
