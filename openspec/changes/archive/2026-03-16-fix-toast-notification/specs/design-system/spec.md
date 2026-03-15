## ADDED Requirements

### Requirement: Toast Notification Component
The system SHALL provide a `<toast-notification>` custom element that displays transient status messages using the Popover API, with each toast as an independent `popover="manual"` element managed by browser-native entry/exit transitions.

#### Scenario: Toast display on event publish
- **WHEN** a `Toast` event is published via `IEventAggregator`
- **THEN** the component SHALL create a new element with `popover="manual"` attribute
- **AND** the element SHALL be made visible via `showPopover()`
- **AND** the toast SHALL display the event's `message` text and an icon matching the `severity`

#### Scenario: Auto-dismiss after duration
- **WHEN** a toast is displayed
- **THEN** the component SHALL call `hidePopover()` after the toast's `durationMs` (default 2500ms)
- **AND** the CSS exit transition SHALL play before the element is removed from the Top Layer

#### Scenario: Programmatic dismiss via handle
- **WHEN** a caller invokes `toast.handle.dismiss()`
- **THEN** `hidePopover()` SHALL be called immediately
- **AND** the auto-dismiss timer SHALL be cleared
- **AND** the `onDismiss` callback SHALL fire exactly once

#### Scenario: DOM cleanup after exit transition
- **WHEN** a toast's `hidePopover()` triggers and the CSS exit transition completes
- **THEN** the popover's `toggle` event SHALL fire with `newState === 'closed'`
- **AND** the component SHALL remove the toast from its internal array
- **AND** the component SHALL NOT rely on `transitionend` events for cleanup

#### Scenario: Multiple simultaneous toasts
- **WHEN** multiple `Toast` events are published in rapid succession
- **THEN** each toast SHALL be an independent popover element in the Top Layer
- **AND** dismissing one toast SHALL NOT interfere with other toasts' transitions or lifecycle
- **AND** toasts SHALL stack vertically in a flex-column layout container

#### Scenario: Toast action button
- **WHEN** a `Toast` event includes an `action` option with `label` and `callback`
- **THEN** the toast SHALL display an action button with the given label
- **AND** clicking the button SHALL invoke the callback and dismiss the toast

#### Scenario: Reduced motion preference
- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** the toast SHALL still be dismissed and removed correctly
- **AND** the browser's `allow-discrete` transition SHALL handle the `display: none` change without animation

#### Scenario: CSS entry animation
- **WHEN** a toast popover is opened via `showPopover()`
- **THEN** the toast SHALL animate from `opacity: 0; transform: translateY(-1rem)` to `opacity: 1; transform: translateY(0)`
- **AND** the entry state SHALL be defined via `@starting-style` inside `:popover-open`

#### Scenario: CSS exit animation
- **WHEN** a toast popover is closed via `hidePopover()`
- **THEN** the toast SHALL animate from `opacity: 1; transform: translateY(0)` to `opacity: 0; transform: translateY(-1rem)`
- **AND** the transition SHALL include `display allow-discrete` and `overlay allow-discrete` to keep the element visible in the Top Layer until the animation completes

#### Scenario: Toast severity visual variants
- **WHEN** a toast has severity `info`
- **THEN** the background SHALL use the brand gradient (`--color-brand-primary` to `--color-brand-secondary`)
- **WHEN** a toast has severity `warning`
- **THEN** the background SHALL use a warm amber gradient
- **WHEN** a toast has severity `error`
- **THEN** the background SHALL use a deep red gradient

#### Scenario: Accessibility
- **WHEN** a toast is displayed
- **THEN** the toast element SHALL have `role="status"` for screen reader announcement
- **AND** the toast SHALL be non-modal (SHALL NOT make background content inert)

#### Scenario: Top Layer stacking with dialogs
- **WHEN** a toast is shown while a `<dialog>` is open via `showModal()`
- **THEN** the toast popover SHALL appear above the dialog because `showPopover()` appends to the top of the Top Layer stack
- **AND** no manual `hidePopover()`/`showPopover()` re-insertion SHALL be needed
