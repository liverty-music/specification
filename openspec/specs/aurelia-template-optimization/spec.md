# Aurelia Template Optimization

## Purpose

Defines the template-level optimization patterns for the Liverty Music frontend, covering keyed list rendering, efficient conditional rendering, class binding syntax, binding behaviors, value converters, and route title configuration using Aurelia 2 best practices.

## Requirements

### Requirement: Keyed list rendering
All `repeat.for` directives SHALL include a `key.bind` expression that uniquely identifies each item.

#### Scenario: Event card list uses key binding
- **WHEN** the `live-highway` component renders event cards via `repeat.for`
- **THEN** each `repeat.for` SHALL include `key.bind` referencing a stable unique identifier (e.g., `ev.id`)
- **AND** the DOM SHALL correctly reconcile when items are added, removed, or reordered

#### Scenario: Static navigation tabs use key binding
- **WHEN** the `bottom-nav-bar` renders tabs via `repeat.for`
- **THEN** the `repeat.for` SHALL include `key.bind` referencing `tab.path`

#### Scenario: Dynamic filter lists use key binding
- **WHEN** the `area-selector-sheet` renders city buttons via `repeat.for`
- **THEN** the `repeat.for` SHALL include `key.bind` referencing a unique city identifier

### Requirement: Switch-based multi-branch conditionals
Multi-branch conditionals with three or more `if.bind` checks on the same expression SHALL use `switch.bind` instead.

#### Scenario: Icon selection uses switch binding
- **WHEN** the `bottom-nav-bar` template selects an SVG icon based on `tab.icon`
- **THEN** the template SHALL use `switch.bind="tab.icon"` with `case` attributes for each icon type
- **AND** a `default-case` SHALL be provided as a fallback

### Requirement: Show binding for frequently toggled elements
UI elements that toggle visibility frequently (more than once per user session on average) SHALL use `show.bind` instead of `if.bind`.

#### Scenario: Bottom navigation bar visibility
- **WHEN** the `bottom-nav-bar` toggles between visible and hidden as the user navigates
- **THEN** the component SHALL use `show.bind="showNav"` to preserve its DOM state
- **AND** the component SHALL NOT be destroyed and recreated on each navigation

#### Scenario: Loading skeleton states
- **WHEN** a component shows a loading skeleton that toggles on each data fetch
- **THEN** the skeleton container SHALL use `show.bind="loading"` instead of `if.bind="loading"`

### Requirement: Class binding syntax for conditional CSS classes
Conditional CSS class application SHALL use Aurelia 2's `.class` binding syntax instead of string interpolation in the `class` attribute.

#### Scenario: Single class toggle
- **WHEN** a single CSS class is conditionally applied based on a boolean expression
- **THEN** the template SHALL use `<className>.class="expression"` syntax
- **AND** the template SHALL NOT use `${condition ? 'className' : ''}` string interpolation

#### Scenario: Multi-class toggle on same condition
- **WHEN** multiple CSS classes are toggled by the same boolean condition
- **THEN** the template SHALL use comma-separated class names: `class-a,class-b.class="condition"`

#### Scenario: Mutually exclusive class groups
- **WHEN** two class groups are toggled by opposite conditions (active vs inactive)
- **THEN** the template SHALL use two `.class` bindings: one for the active classes and one for the inactive classes with a negated condition

### Requirement: Debounce binding behavior on search inputs
Text input fields that trigger search, filter, or API calls SHALL use the `& debounce` binding behavior.

#### Scenario: Artist search debounce
- **WHEN** the user types in the artist search input on `discover-page`
- **THEN** the binding SHALL include `& debounce:300` to delay processing until 300ms after the last keystroke

#### Scenario: Area search debounce
- **WHEN** the user types in the city search input on `area-selector-sheet`
- **THEN** the binding SHALL include `& debounce:300`

### Requirement: Throttle binding behavior on continuous event handlers
Event handlers for continuous user interactions (touch move, scroll, resize) SHALL use the `& throttle` binding behavior.

#### Scenario: Swipe gesture throttle
- **WHEN** the `my-artists-page` handles `touchmove` events for swipe gestures
- **THEN** the event binding SHALL include `& throttle:16` (one frame at 60fps)

### Requirement: Date value converter
A reusable date value converter SHALL be provided for formatting date/time values in templates.

#### Scenario: Short date format
- **WHEN** a template renders a date with `${event.date | date:'short'}`
- **THEN** the converter SHALL output a localized short date string (e.g., "2/25" for ja-JP)

#### Scenario: Long date format
- **WHEN** a template renders a date with `${event.date | date:'long'}`
- **THEN** the converter SHALL output a localized long date string (e.g., "2026年2月25日")

#### Scenario: Relative time format
- **WHEN** a template renders a date with `${event.date | date:'relative'}`
- **THEN** the converter SHALL output a relative time string (e.g., "3日後", "2時間前")

### Requirement: Route title configuration
All route definitions SHALL include a `title` property for document title management.

#### Scenario: Route title applied
- **WHEN** the user navigates to a route (e.g., Dashboard)
- **THEN** the document title SHALL update to include the route's title (e.g., "Dashboard - Liverty Music")

#### Scenario: Fallback title
- **WHEN** the user navigates to the not-found page
- **THEN** the document title SHALL display "Not Found - Liverty Music"
