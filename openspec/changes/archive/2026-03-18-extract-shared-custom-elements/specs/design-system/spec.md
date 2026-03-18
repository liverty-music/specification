## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: State Placeholder Component — title and description bindables
**Reason**: Replaced by `<au-slot>` content projection. The `title`, `description`, and `ctaLabel` bindables are redundant with slotted content and add unnecessary API surface.
**Migration**: Replace `<state-placeholder title="X" description="Y">` with `<state-placeholder icon="..."><h2>X</h2><p>Y</p></state-placeholder>`.

## MODIFIED Requirements

### Requirement: Toast Notification Component
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

## RENAMED Requirements

### Requirement: Toast Notification Component
- **FROM:** Toast Notification Component (`<toast-notification>`)
- **TO:** Snack Bar Component (`<snack-bar>`)

### Requirement: Toast event class
- **FROM:** `Toast` class in `toast.ts`
- **TO:** `Snack` class in `snack.ts`
