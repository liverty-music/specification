# Snack Bar

## Purpose

Provides a persistent snack bar that notifies the user when an app update is ready to install, with a prominent action to apply it.

## Requirements

### Requirement: Snack Bar Component
The system SHALL provide a `<snack-bar>` custom element (renamed from `<toast-notification>`) that displays transient status messages using the Popover API, with each snack as an independent `popover="manual"` element managed by browser-native entry/exit transitions. A snack's display time follows the Material 3 snackbar durations: a snack without an action SHALL stay 4 seconds when its message is at most 30 characters and 10 seconds when it is longer, a snack with an action SHALL stay 10 seconds, and a snack that sets its own duration SHALL keep it.

#### Scenario: Snack display on event publish
- **WHEN** a `Snack` event is published via `IEventAggregator`
- **THEN** the component SHALL create a new element with `popover="manual"` attribute
- **AND** the element SHALL be made visible via `showPopover()`
- **AND** the snack SHALL display the event's `message` text and an icon matching the `severity`

#### Scenario: Auto-dismiss after duration
- **WHEN** a snack is displayed
- **THEN** the component SHALL call `hidePopover()` after the snack's display time
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
- **THEN** the snack SHALL rise into place from below, animating from `opacity: 0; transform: translateY(1rem)` to `opacity: 1; transform: translateY(0)`
- **AND** the entry state SHALL be defined via `@starting-style` inside `:popover-open`

#### Scenario: CSS exit animation
- **WHEN** a snack popover is closed via `hidePopover()`
- **THEN** the snack SHALL sink out of place, animating from `opacity: 1; transform: translateY(0)` to `opacity: 0; transform: translateY(1rem)`
- **AND** the transition SHALL include `display allow-discrete` and `overlay allow-discrete` to keep the element visible in the Top Layer until the animation completes

#### Scenario: Snack severity visual variants
- **WHEN** a snack has severity `info`
- **THEN** the background SHALL use a gradient in the brand hues (from brand-primary's hue to brand-secondary's), darkened so that white text meets 4.5:1 across it
- **WHEN** a snack has severity `warning`
- **THEN** the background SHALL use a deep amber gradient, dark enough that white text meets 4.5:1 across it
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

#### Scenario: Short message
- **WHEN** a snack without an action shows 「パスキーを追加しました。」 (12 characters)
- **THEN** it SHALL be dismissed 4 seconds after it appears

#### Scenario: Long message
- **WHEN** a snack without an action shows a message of 50 characters
- **THEN** it SHALL be dismissed 10 seconds after it appears

#### Scenario: Snack with its own duration
- **WHEN** a snack is published with its own duration (for example the update snack, which never auto-dismisses)
- **THEN** that duration SHALL be used

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

### Requirement: The update action stands out as a button on the snack bar

When the update snack is displayed, its action button (labelled with `pwa.updateAction`) SHALL be visually distinguished from the snack body text so that users immediately identify it as a button. The button SHALL use the on-container button style in the compact snack-bar size (see UI Primitives): a translucent white fill, a white border and the shared button corner radius. When the update snack appears, the button SHALL glow three times and then stay still for as long as the snack is shown. The glow SHALL NOT play when `prefers-reduced-motion: reduce` is active. The update snack SHALL show no leading icon, so its message (「新しいバージョンがあります」) and action fit one row on a 360px screen.

#### Scenario: Action button appears in the on-container style
- **WHEN** the update snack is visible with the action button
- **THEN** the action button SHALL have a white border at least 1.5px wide and a translucent white fill
- **AND** its corner radius SHALL equal the shared button corner radius (12px)

#### Scenario: The glow plays three times, then stops
- **WHEN** the update snack appears
- **THEN** the action button SHALL glow exactly three times
- **AND** after the third glow the button SHALL remain still while the snack stays open

#### Scenario: Animation is suppressed under reduced motion
- **WHEN** the user's OS has `prefers-reduced-motion: reduce` set
- **THEN** the glow SHALL NOT play
- **AND** the border and fill SHALL still be applied

#### Scenario: No leading icon
- **WHEN** the update snack is visible
- **THEN** it SHALL show no leading icon
- **AND** on a 360px-wide screen its message SHALL fit one line beside the action

### Requirement: Snack text meets WCAG AA contrast

Every snack bar's message and its action label SHALL keep a contrast ratio of at least 4.5:1 against the container colour behind them at every point of the container's gradient, for every severity. This applies to the action's own fill as well: the on-container action's translucent white fill over the gradient. The minimum SHALL be met by the container colours and SHALL NOT depend on the text being large. The brand colours used by other surfaces (the FAB, the navigation bar, the filled button) SHALL NOT change for this.

#### Scenario: Message contrast on every severity
- **WHEN** an info, a warning and an error snack bar are each shown
- **THEN** the white message SHALL measure at least 4.5:1 against every point of that snack's container gradient, both ends included

#### Scenario: Action contrast on every severity
- **WHEN** a snack bar with an action (such as the update snack) is shown in each severity
- **THEN** the action's label SHALL measure at least 4.5:1 against the action's translucent fill laid over every point of the container gradient, both ends included

### Requirement: Snack bars sit above the bottom navigation and any banner

Every snack bar, whatever its severity or sender, SHALL be placed at the bottom of the screen with its bottom edge one `space-s` step above the top of the bottom navigation bar and the bottom safe-area inset. While a persistent bottom banner (the signup prompt or the install banner) is visible above the navigation bar, the snack bar SHALL sit that same step above the banner instead, using the banner's rendered height; a banner that is not visible SHALL add no height. The FAB stays sunk in the navigation bar in both cases (see FAB Menu).

#### Scenario: No banner is visible
- **WHEN** a snack bar opens and no persistent bottom banner is visible
- **THEN** the gap between the snack bar's bottom edge and the navigation bar's top edge SHALL be one `space-s` step (16 to 20px)

#### Scenario: A hidden banner adds no height
- **WHEN** a banner's host is on the screen but the banner is not visible (the app is installed, or a post-signup surface hides it)
- **AND** a snack bar opens
- **THEN** the snack bar SHALL sit one `space-s` step above the navigation bar

#### Scenario: A banner is visible
- **WHEN** a snack bar opens while the signup prompt or the install banner is visible
- **THEN** the snack bar's bottom edge SHALL sit one `space-s` step above the banner's top edge
- **AND** the snack bar SHALL NOT cover any part of the banner

#### Scenario: The FAB stays sunk under a banner and a snack bar
- **WHEN** a snack bar opens while a bottom banner is visible on a route that shows the FAB
- **THEN** the FAB SHALL stay sunk in the navigation bar
- **AND** the snack bar SHALL cover neither the FAB nor the banner

#### Scenario: Same placement for every severity
- **WHEN** an info, warning and error snack bar are each shown in turn under the same conditions
- **THEN** all three SHALL occupy the same vertical position
