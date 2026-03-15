## NEW Requirements

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
