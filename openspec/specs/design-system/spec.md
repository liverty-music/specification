# Design System

## Purpose

Defines the centralized design token system and visual foundation for the Liverty Music application, ensuring consistency across all screens through plain CSS custom properties in `tokens.css`, a dark-first theme, and optimized display font loading.

## Requirements

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

---

### Requirement: Display Font Loading
The system SHALL load and apply display and body fonts with appropriate fallback and performance optimization.

#### Scenario: Font preloading
- **WHEN** the application loads
- **THEN** the system SHALL preconnect to the font provider domains (fonts.googleapis.com and fonts.gstatic.com) in the HTML head
- **AND** the preconnect to `fonts.gstatic.com` SHALL include the `crossorigin` attribute
- **AND** the system SHALL load Righteous (weight 400) and Poppins (weights 300, 400, 500, 600, 700) with `font-display: swap`
- **AND** the existing Outfit font `<link>` SHALL be retained as a fallback for `--font-display`
- **AND** the system SHALL use Outfit as the second fallback for `--font-display` and system-ui as the fallback for `--font-body`

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

#### Scenario: Rendering with icon only
- **WHEN** `<state-placeholder icon="music">` is rendered with slotted content
- **THEN** the component SHALL display an xl-sized svg-icon
- **AND** the slotted content SHALL be projected via `<au-slot>` below the icon
- **AND** the content SHALL be vertically and horizontally centered

#### Scenario: No icon
- **WHEN** `<state-placeholder>` is rendered without an `icon` attribute
- **THEN** no svg-icon SHALL be rendered
- **AND** only the slotted content SHALL be displayed

#### Scenario: Custom content via slot
- **WHEN** child content is placed inside `<state-placeholder>`
- **THEN** the content SHALL be projected via `<au-slot>`
- **AND** this SHALL allow pages to provide titles, descriptions, buttons, links, or `<loading-spinner>` elements

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

---

### Requirement: Snack Bar Component
The system SHALL provide a `<snack-bar>` custom element (renamed from `<toast-notification>`) that displays transient status messages using the Popover API, with each snack as an independent `popover="manual"` element managed by browser-native entry/exit transitions.

#### Scenario: Snack display on event publish
- **WHEN** a `Snack` event is published via `IEventAggregator`
- **THEN** the component SHALL create a new element with `popover="manual"` attribute
- **AND** the element SHALL be made visible via `showPopover()`
- **AND** the snack SHALL display the event's `message` text and an icon matching the `severity`

#### Scenario: Auto-dismiss after duration
- **WHEN** a snack is displayed
- **THEN** the component SHALL call `hidePopover()` after the snack's `durationMs` (default 2500ms)
- **AND** the CSS exit transition SHALL play before the element is removed from the Top Layer

#### Scenario: Programmatic dismiss via handle
- **WHEN** a caller invokes `snack.handle.dismiss()`
- **THEN** `hidePopover()` SHALL be called immediately
- **AND** the auto-dismiss timer SHALL be cleared
- **AND** the `onDismiss` callback SHALL fire exactly once

#### Scenario: DOM cleanup after exit transition
- **WHEN** a snack's `hidePopover()` triggers and the CSS exit transition completes
- **THEN** the popover's `toggle` event SHALL fire with `newState === 'closed'`
- **AND** the component SHALL remove the snack from its internal array
- **AND** the component SHALL NOT rely on `transitionend` events for cleanup

#### Scenario: Multiple simultaneous snacks
- **WHEN** multiple `Snack` events are published in rapid succession
- **THEN** each snack SHALL be an independent popover element in the Top Layer
- **AND** dismissing one snack SHALL NOT interfere with other snacks' transitions or lifecycle
- **AND** snacks SHALL stack vertically in a flex-column layout container

#### Scenario: Snack action button
- **WHEN** a `Snack` event includes an `action` option with `label` and `callback`
- **THEN** the snack SHALL display an action button with the given label
- **AND** clicking the button SHALL invoke the callback and dismiss the snack

#### Scenario: Reduced motion preference
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** the snack SHALL still be dismissed and removed correctly
- **AND** a `@media (prefers-reduced-motion: reduce)` CSS rule SHALL set `transition-duration: 0s` on `.snack-item` to suppress animation

#### Scenario: CSS entry animation
- **WHEN** a snack popover is opened via `showPopover()`
- **THEN** the snack SHALL animate from `opacity: 0; transform: translateY(-1rem)` to `opacity: 1; transform: translateY(0)`
- **AND** the entry state SHALL be defined via `@starting-style` inside `:popover-open`

#### Scenario: CSS exit animation
- **WHEN** a snack popover is closed via `hidePopover()`
- **THEN** the snack SHALL animate from `opacity: 1; transform: translateY(0)` to `opacity: 0; transform: translateY(-1rem)`
- **AND** the transition SHALL include `display allow-discrete` and `overlay allow-discrete` to keep the element visible in the Top Layer until the animation completes

#### Scenario: Snack severity visual variants
- **WHEN** a snack has severity `info`
- **THEN** the background SHALL use the brand gradient (`--color-brand-primary` to `--color-brand-secondary`)
- **WHEN** a snack has severity `warning`
- **THEN** the background SHALL use a warm amber gradient
- **WHEN** a snack has severity `error`
- **THEN** the background SHALL use a deep red gradient

#### Scenario: Accessibility
- **WHEN** a snack is displayed
- **THEN** the snack element SHALL have `role="status"` for screen reader announcement
- **AND** the snack SHALL be non-modal (SHALL NOT make background content inert)

#### Scenario: Top Layer stacking with dialogs
- **WHEN** a snack is shown while a `<dialog>` is open via `showModal()`
- **THEN** the snack popover SHALL appear above the dialog because `showPopover()` appends to the top of the Top Layer stack
- **AND** no manual `hidePopover()`/`showPopover()` re-insertion SHALL be needed
