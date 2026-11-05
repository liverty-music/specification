## MODIFIED Requirements

### Requirement: Snack Bar Component
The system SHALL provide a `<snack-bar>` custom element (renamed from `<toast-notification>`) that displays transient status messages using the Popover API, with each snack as an independent `popover="manual"` element managed by browser-native entry/exit transitions. A snack's display time follows the Material 3 snackbar durations: a snack without an action SHALL stay 4 seconds when its message is at most 30 characters and 10 seconds when it is longer, a snack with an action SHALL stay 10 seconds, and a snack that sets its own duration SHALL keep it. A dismissed snack SHALL stay on screen until its exit motion has ended, and the snacks on screen SHALL stack upward from the oldest one without overlapping.

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
- **WHEN** a snack is dismissed by its timer, its handle, its action, its close button or a swipe
- **THEN** the snack SHALL stay in the document, sinking and fading out, until its exit transition has ended
- **AND** only then SHALL it be removed
- **AND** the popover's `toggle` event SHALL NOT be taken as the end of the exit motion, because it fires when `hidePopover()` is called

#### Scenario: Multiple simultaneous snacks
- **WHEN** multiple `Snack` events are published in rapid succession
- **THEN** each snack SHALL be an independent popover element in the Top Layer
- **AND** dismissing one snack SHALL NOT interfere with other snacks' transitions or lifecycle
- **AND** the oldest open snack SHALL sit lowest, and each newer snack SHALL sit directly above the one opened before it, separated by one `space-3xs` step, so a new snack never moves the snacks already on screen
- **AND** when a lower snack leaves, the snacks above it SHALL move down into its place

#### Scenario: Open snacks never overlap
- **WHEN** three snacks are open at once, one of them with a two-line message
- **THEN** no two snacks' boxes SHALL overlap
- **AND** the lowest snack SHALL keep the placement stated in "Snack bars sit above the bottom navigation and any banner"

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

## ADDED Requirements

### Requirement: A horizontal swipe dismisses a snack
A fan SHALL be able to dismiss any snack by swiping it left or right. While a finger or pointer holds a snack, its display timer SHALL pause, and it SHALL resume with the time that was left when the snack is released without being dismissed. A snack whose swipe does not reach the dismiss point SHALL return to its place. A dismiss by swipe SHALL be the same as any other dismiss: its `onDismiss` callback fires once, so an undo window closes and commits, and the exit motion plays.

#### Scenario: Swipe past the dismiss point
- **WHEN** the fan drags a snack sideways until less than half of it remains in its place and releases it
- **THEN** the snack SHALL leave in the direction of the swipe and be dismissed
- **AND** its `onDismiss` callback SHALL fire exactly once

#### Scenario: Short swipe
- **WHEN** the fan drags a snack sideways by less than half its width and releases it
- **THEN** the snack SHALL return to its place and stay open

#### Scenario: Holding pauses the timer
- **WHEN** a 4-second snack has been shown for 3 seconds and the fan then holds it for 5 seconds without dismissing it
- **THEN** the snack SHALL still be open when released
- **AND** it SHALL be dismissed 1 second after it is released

#### Scenario: Swipe on a snack that stays until the fan acts
- **WHEN** the fan swipes away the app update snack
- **THEN** the snack SHALL be dismissed and the update SHALL NOT be applied

#### Scenario: Swipe under reduced motion
- **WHEN** `prefers-reduced-motion: reduce` is active and the fan swipes a snack past the dismiss point
- **THEN** the snack SHALL be dismissed and removed without an exit motion
