## ADDED Requirements

### Requirement: CUBE CSS layer ordering via `@layer`
The application SHALL declare a global CSS layer order that enforces the CUBE CSS cascade hierarchy. All styles MUST reside within an explicit `@layer` block.

#### Scenario: Layer order declared in main.css
- **WHEN** `src/styles/main.css` is loaded
- **THEN** the file SHALL declare `@layer reset, tokens, global, composition, utility, block, exception;` as the first statement
- **AND** each subsequent `@import` SHALL specify which layer it belongs to via `layer()` syntax

#### Scenario: No styles outside @layer
- **WHEN** stylelint runs against any CSS file in the project
- **THEN** the `cube/require-layer` rule SHALL report zero warnings
- **AND** every style rule, `@keyframes`, and `@media` block SHALL be nested inside an `@layer` block

---

### Requirement: CSS entry point at `src/styles/main.css`
The application SHALL use `src/styles/main.css` as the single CSS entry point, imported from `main.ts`.

#### Scenario: main.ts imports main.css
- **WHEN** the application bootstraps via `main.ts`
- **THEN** `main.ts` SHALL contain `import './styles/main.css'`
- **AND** `main.css` SHALL import all global style files (tokens, reset, global, compositions, utilities) in layer order

#### Scenario: main.css imports in correct order
- **WHEN** `main.css` is parsed by the browser
- **THEN** the imports SHALL follow this order:
  1. `reset.css` in `layer(reset)`
  2. `tokens.css` in `layer(tokens)`
  3. `global.css` in `layer(global)`
  4. `compositions.css` in `layer(composition)`
  5. `utilities.css` in `layer(utility)`

---

### Requirement: Design tokens in `tokens.css` as plain CSS custom properties
The application SHALL define all design tokens as CSS custom properties in `src/styles/tokens.css`, without dependency on any CSS framework's token system.

#### Scenario: Token file contains all design tokens
- **WHEN** `tokens.css` is loaded
- **THEN** it SHALL define custom properties for colors (`--color-brand-*`, `--color-surface-*`, `--color-text-*`), typography (`--font-display`, `--font-body`), spacing scale (`--space-3xs` through `--space-3xl`), radii (`--radius-*`), shadows (`--shadow-*`), container breakpoints (`--container-*`), and transition tokens (`--transition-*`)

#### Scenario: Token values use OKLCH color model
- **WHEN** color tokens are defined
- **THEN** all color values SHALL use `oklch()` notation
- **AND** no `rgb()`, `hsl()`, or hex notation SHALL appear

---

### Requirement: Browser reset in `reset.css` using `:where()` for zero specificity
The application SHALL use a custom CSS reset that normalizes browser defaults with zero specificity so that any subsequent layer can override without specificity conflicts.

#### Scenario: Reset uses :where() wrapper
- **WHEN** `reset.css` is loaded inside `@layer reset`
- **THEN** all selectors SHALL be wrapped in `:where()` pseudo-class
- **AND** the reset SHALL include: `box-sizing: border-box` on all elements, `margin: 0` on all elements, `display: block; max-inline-size: 100%` on media elements, `font: inherit` on form elements, and `min-block-size: 100dvh` on `body`

#### Scenario: Reset has zero specificity
- **WHEN** any rule in a higher layer (global, block, etc.) targets the same element
- **THEN** the higher-layer rule SHALL win without needing increased specificity
- **AND** no `!important` SHALL be required to override reset styles

---

### Requirement: Global layer for base element styling
The `global.css` file SHALL define default styles for bare HTML elements following the CUBE CSS principle of "do as much as you can in the global CSS."

#### Scenario: Bare elements are visually correct without classes
- **WHEN** an HTML page contains bare `body`, `h1`-`h6`, `p`, `a`, `button`, `input`, `svg` elements with no class attributes
- **THEN** each element SHALL have appropriate default styling from `@layer global`
- **AND** `body` SHALL have the dark theme background (`--color-surface-base`) and primary text color (`--color-text-primary`)
- **AND** `h1`-`h6` SHALL use the display font (`--font-display`) with a fluid type scale via `clamp()`
- **AND** `a` elements SHALL have a visible, accessible default style
- **AND** `button` elements SHALL have a base interactive style (cursor, padding, border-radius from tokens)

#### Scenario: View transitions defined in global layer
- **WHEN** a route change occurs
- **THEN** `::view-transition-old(root)` and `::view-transition-new(root)` styles SHALL be defined in `@layer global`
- **AND** transition values SHALL reference design tokens (`--transition-route-duration`, `--transition-route-easing`)

---

### Requirement: Composition layer for layout primitives
The `compositions.css` file SHALL provide reusable layout classes that control spatial relationships between child elements.

#### Scenario: Flow composition (vertical rhythm)
- **WHEN** elements need vertical rhythm with consistent spacing between siblings
- **THEN** the `.flow` class SHALL provide vertical spacing via `> * + * { margin-block-start: var(--flow-space, 1em) }`
- **AND** the spacing SHALL be customizable via `--flow-space` custom property on any descendant

#### Scenario: Stack composition
- **WHEN** elements need vertical stacking with consistent spacing via flexbox
- **THEN** the `.stack` class SHALL provide `display: flex; flex-direction: column; gap: var(--space-m)`
- **AND** the gap SHALL be customizable via `--stack-gap` custom property

#### Scenario: Cluster composition
- **WHEN** elements need horizontal inline grouping with wrapping
- **THEN** the `.cluster` class SHALL provide `display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-s)`
- **AND** the gap SHALL be customizable via `--cluster-gap` custom property

#### Scenario: Center composition
- **WHEN** content needs centering within its container
- **THEN** the `.center` class SHALL provide centering with `margin-inline: auto` and a configurable `max-inline-size`

#### Scenario: Wrapper composition
- **WHEN** content needs a max-width constraint with horizontal padding
- **THEN** the `.wrapper` class SHALL provide `max-inline-size: var(--wrapper-max, 65ch); padding-inline: var(--gutter, var(--space-m)); margin-inline: auto`

#### Scenario: Compositions contain no visual properties
- **WHEN** stylelint runs against `compositions.css`
- **THEN** the `cube/no-visual-in-composition` rule SHALL report zero warnings
- **AND** no `color`, `background`, `border`, `shadow`, `font-*`, or `text-*` properties SHALL appear in composition classes

---

### Requirement: Utility layer for single-purpose overrides
The `utilities.css` file SHALL provide single-purpose utility classes that each control exactly one CSS property or concern.

#### Scenario: Animation keyframes and utility classes
- **WHEN** a component needs a shared animation
- **THEN** `@keyframes` definitions (fade-in, fade-out, fade-slide-up, modal-enter, hype-pulse, bounce-in) SHALL be defined in `@layer utility`
- **AND** corresponding `.animate-*` utility classes SHALL apply the animation with a single `animation` shorthand

#### Scenario: Reduced motion override
- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** a utility-layer `@media` rule SHALL disable all animations on `.animate-*` classes and view transitions

#### Scenario: Utilities limited to single property
- **WHEN** stylelint runs against `utilities.css`
- **THEN** the `cube/utility-single-property` rule SHALL report zero warnings

---

### Requirement: Block layer for component-scoped styles
Each component's colocated CSS file SHALL wrap its styles in `@layer block { @scope(<element-selector>) { ... } }`.

#### Scenario: Component CSS uses @scope
- **WHEN** a component CSS file (e.g., `event-card.css`) is loaded
- **THEN** all styles SHALL be inside `@layer block { @scope(event-card) { ... } }`
- **AND** styles SHALL not leak to elements outside the component's scope

#### Scenario: Block files limited to ~80 lines
- **WHEN** stylelint runs against a component CSS file
- **THEN** the `cube/block-max-lines` rule SHALL report zero warnings for each `@scope` block
- **AND** if a block exceeds the limit, styles SHALL be refactored — extracting shared patterns to composition or utility layers

#### Scenario: One block per file
- **WHEN** stylelint runs against a component CSS file
- **THEN** the `cube/one-block-per-file` rule SHALL report zero warnings
- **AND** each `.css` file SHALL contain at most one `@scope` block

---

### Requirement: Exception layer for state deviations via `data-*` attributes
Component state variations SHALL use `data-*` attributes (not CSS class toggling) to drive styling, as enforced by the `cube/exception-data-attr` rule.

#### Scenario: State-driven styling uses data attributes
- **WHEN** a component has visual state variations (e.g., active, disabled, loading)
- **THEN** the variations SHALL be expressed via `data-state`, `data-variant`, or `data-theme` attributes
- **AND** CSS selectors SHALL target `[data-state="active"]` etc. within `@layer exception` or within `@layer block` using `data-*` attribute selectors

#### Scenario: Stylelint enforces data attribute convention
- **WHEN** stylelint runs against all CSS files
- **THEN** the `cube/exception-data-attr` and `cube/data-attr-naming` rules SHALL report zero warnings

---

### Requirement: Spacing controlled by parent, not child
Layout spacing SHALL follow the CUBE CSS principle where parent elements control inter-child spacing via `gap`, and children SHALL NOT set external margins.

#### Scenario: No child margin for spacing
- **WHEN** a layout needs spacing between sibling elements
- **THEN** the parent SHALL use `gap` (grid or flex) or the `.stack` / `.cluster` composition
- **AND** child elements SHALL NOT use `margin-block-start`, `margin-block-end`, or equivalent properties for inter-sibling spacing

#### Scenario: Internal padding uses fluid values
- **WHEN** a component needs internal spacing
- **THEN** `padding` SHALL use `clamp()` or CSS custom properties from the spacing scale
- **AND** fixed pixel values for padding SHALL be avoided in favor of fluid, token-based values

---

### Requirement: No TailwindCSS dependency
The application SHALL not depend on TailwindCSS for any styling functionality.

#### Scenario: No Tailwind in build pipeline
- **WHEN** the application builds via Vite
- **THEN** `vite.config.ts` SHALL NOT import or register `@tailwindcss/vite`
- **AND** no CSS file SHALL contain `@import "tailwindcss"`

#### Scenario: No Tailwind packages in dependencies
- **WHEN** `package.json` is inspected
- **THEN** neither `tailwindcss` nor `@tailwindcss/vite` SHALL appear in `dependencies` or `devDependencies`

#### Scenario: No Tailwind utility classes in HTML
- **WHEN** any HTML template file is inspected
- **THEN** no Tailwind-generated utility class names (e.g., `flex`, `px-4`, `text-white`, `bg-surface-base`, `hover:bg-white/5`) SHALL appear in `class` attributes
