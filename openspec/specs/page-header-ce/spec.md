# page-header-ce Specification

## Purpose

The Page Header capability provides a reusable custom element that renders a consistent header across route pages, supporting i18n titles, optional trailing actions via slots, and automatic grid layout integration.

## Requirements

### Requirement: Page header renders i18n title
The `page-header` CE SHALL render a `<header>` element containing an `<h1>` whose text content is resolved from the `title-key` bindable via the i18n `t` binding.

#### Scenario: Title-only header (settings, tickets)
- **WHEN** `<page-header title-key="settings.title"></page-header>` is used with no slot content
- **THEN** the header renders `<h1>` with the translated text for `settings.title` and no additional child elements

#### Scenario: Title key changes dynamically
- **WHEN** the `title-key` bindable value changes at runtime
- **THEN** the `<h1>` text updates to reflect the new translation

### Requirement: Page header supports trailing actions via slot
The `page-header` CE SHALL provide a default `<au-slot>` after the `<h1>` element for optional trailing content (badges, buttons).

#### Scenario: Header with slotted actions (my-artists)
- **WHEN** `<page-header title-key="nav.myArtists"><span class="artist-count">(...)</span><button>...</button></page-header>` is used
- **THEN** the `<h1>` is followed by the slotted `<span>` and `<button>`, laid out inline via flexbox with the title taking remaining space

#### Scenario: No slot content provided
- **WHEN** `<page-header title-key="nav.tickets"></page-header>` is used without children
- **THEN** the header renders only the `<h1>` with no extra whitespace or empty wrapper

### Requirement: Page header provides consistent visual styling
The `page-header` CE SHALL encapsulate the shared header styles: padding, bottom border, background color, and `<h1>` typography (font-family, size, weight, letter-spacing).

#### Scenario: Visual consistency across routes
- **WHEN** `page-header` is rendered in my-artists, settings, and tickets routes
- **THEN** all three headers share identical padding (`--space-xs`), border (`1px solid` at 10% white), background (`--color-surface-raised`), and `<h1>` typography

### Requirement: Page header participates in route grid layout
The `page-header` CE host element SHALL set `grid-area: header` so it integrates with the route's `grid-template-areas` without additional route-level CSS.

#### Scenario: Header placed in grid area
- **WHEN** a route defines `grid-template-areas: "header" "content"`
- **THEN** the `page-header` CE occupies the `header` grid area automatically

### Requirement: Page header is globally registered
The `PageHeader` class SHALL be registered globally in `main.ts` so all routes can use `<page-header>` without per-route `<import>` statements.

#### Scenario: Usage without explicit import
- **WHEN** a route template uses `<page-header title-key="...">` without an `<import>` tag
- **THEN** the component resolves and renders correctly
