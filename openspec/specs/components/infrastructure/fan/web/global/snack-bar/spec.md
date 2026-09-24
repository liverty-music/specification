# Snack Bar

## Purpose

Provides a persistent snack bar that notifies the user when an app update is ready to install, with a prominent action to apply it.

## Requirements

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

### Requirement: The SPA shows a persistent update toast when a waiting SW is detected after user interaction

When `vite-plugin-pwa` detects a waiting SW (`onNeedRefresh` callback) after the user has begun interacting with the page, the SPA SHALL publish a non-auto-dismissing `Snack` notification with an action button that, when tapped, sends `SKIP_WAITING` to the waiting SW, triggering a `controllerchange` event and a single-shot page reload.

#### Scenario: Update toast shown after user interaction

- **WHEN** a new Service Worker reaches the `installed` (waiting) state
- **AND** the user has already performed at least one pointer or keyboard interaction with the page
- **THEN** the SPA SHALL publish a `Snack` event via `IEventAggregator` with:
  - severity: `info`
  - `duration: Infinity` (no auto-dismiss)
  - an `action` button labelled with the i18n key `pwa.updateAction`
- **AND** at most one update `Snack` SHALL be active at a time

#### Scenario: Tapping the update action triggers reload

- **WHEN** the user taps the [更新] action on the update Snack
- **THEN** `updateSW(true)` SHALL be called (dispatches `SKIP_WAITING` to the waiting SW)
- **AND** the page SHALL reload exactly once via `controllerchange`
- **AND** after reload the page SHALL be controlled by the new Service Worker

#### Scenario: No duplicate reloads (reloop guard)

- **WHEN** `controllerchange` fires
- **THEN** `location.reload()` SHALL be called at most once per lifecycle
- **AND** a subsequent `controllerchange` event (e.g., from another tab's skipWaiting) SHALL NOT trigger a second reload on the same page

### Requirement: The update action button is visually prominent

When the update snack is displayed, its action button (labelled with `pwa.updateAction`) SHALL be visually distinguished from the snack body text so that users can immediately identify it as a primary call-to-action. The button SHALL use a pill-shaped border and a pulsing glow animation to attract attention. The animation SHALL be suppressed when `prefers-reduced-motion: reduce` is active.

#### Scenario: Action button appears as a pill with pulse animation

- **WHEN** the update snack is visible with the action button
- **THEN** the action button SHALL have a rounded pill border (1.5px, semi-transparent white)
- **AND** a semi-transparent white background fill SHALL distinguish it from plain text
- **AND** the button SHALL animate a repeating `box-shadow` glow pulse (period ≈ 1.8s, ease-in-out)

#### Scenario: Animation is suppressed under reduced motion

- **WHEN** the user's OS has `prefers-reduced-motion: reduce` set
- **THEN** the pulse animation SHALL NOT play
- **AND** the pill border and background fill SHALL still be applied (static emphasis)

### Requirement: Fire-and-forget failures show a snack and revert optimistic UI
The system SHALL replace silent error swallowing in services with explicit error states that callers can distinguish from empty-data states.

#### Scenario: Service method returns error result instead of empty fallback
- **WHEN** a service method fails to fetch data from the backend
- **THEN** the method SHALL throw the error to the caller (not silently return an empty array or false)
- **AND** the caller SHALL handle the error via `promise.bind` catch block or explicit try/catch with user feedback

#### Scenario: Fire-and-forget operations provide user feedback on failure
- **WHEN** a fire-and-forget RPC operation (e.g., artist follow) fails
- **THEN** the system SHALL display an error snack informing the user of the failure
- **AND** the system SHALL revert any optimistic UI updates
