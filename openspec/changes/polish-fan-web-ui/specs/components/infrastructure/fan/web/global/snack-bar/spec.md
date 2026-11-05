## MODIFIED Requirements

### Requirement: Snack Bar Component
The system SHALL provide a `<snack-bar>` custom element (renamed from `<toast-notification>`) that displays transient status messages using the Popover API, with each snack as an independent `popover="manual"` element managed by browser-native entry/exit transitions. A snack's display time follows the Material 3 snackbar durations: a snack without an action SHALL stay 4 seconds when its message is at most 30 characters and 10 seconds when it is longer, a snack with an action SHALL stay 10 seconds, and a snack that sets its own duration SHALL keep it. A dismissed snack SHALL stay on screen until its exit motion has ended. The fan app shows one snack at a time (see "Snacks appear one at a time").

#### Scenario: Snack display on event publish
- **WHEN** a `Snack` event is published via `IEventAggregator`
- **THEN** the component SHALL create a new element with `popover="manual"` attribute once it is the snack's turn (see "Snacks appear one at a time")
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

#### Scenario: Multiple simultaneous snacks
- **WHEN** multiple `Snack` events are published in rapid succession
- **THEN** each snack, when it appears, SHALL be an independent popover element in the Top Layer
- **AND** dismissing one snack SHALL NOT interfere with another snack's transitions or lifecycle
- **AND** the snacks SHALL appear one after another, as "Snacks appear one at a time" states, never two in the same place

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

### Requirement: Snack bars sit above the bottom navigation and any banner

Every snack bar, whatever its severity or sender, SHALL be placed at the bottom of the screen with its bottom edge one `space-s` step above the top of the bottom navigation bar and the bottom safe-area inset. While a persistent bottom banner (the signup prompt or the install banner) is visible above the navigation bar, the snack bar SHALL sit that same step above the banner instead, using the banner's rendered height; a banner that is not visible SHALL add no height. While a screen shows a control floating over its bottom edge (the Discovery swap tile), the snack bar SHALL sit one `space-3xs` step above that control instead, and the control SHALL NOT move; such a control always sits above any visible banner, so this placement takes precedence over the banner placement. The FAB stays sunk in the navigation bar in all cases (see FAB Menu).

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

#### Scenario: A banner and a floating control are both visible
- **WHEN** a snack bar opens on Discovery while the install banner and the swap tile are both visible
- **THEN** the snack bar's bottom edge SHALL sit one `space-3xs` step above the swap tile's top edge
- **AND** the snack bar SHALL cover neither the swap tile nor the banner

#### Scenario: A floating control stays in place
- **WHEN** a snack bar opens on Discovery while the swap tile is shown
- **THEN** the snack bar's bottom edge SHALL sit one `space-3xs` step above the swap tile's top edge
- **AND** the swap tile SHALL stay where it was and stay tappable

## ADDED Requirements

### Requirement: Snacks appear one at a time

In the fan app, at most one snack SHALL be visible at a time. A snack published while another is visible SHALL wait, and the waiting snacks SHALL appear in the order they were published, each after the one before it has finished its exit motion. A snack that a sender marks as replacing its own earlier snack SHALL take that snack's place: a visible one is dismissed at once and the new snack appears next, and a waiting one is replaced where it waits. The app update snack, which stays until the fan acts, SHALL give way to every other snack: when another snack is published while it is visible, it SHALL leave without being dismissed and SHALL appear again when no other snack is visible or waiting. A snack with an action, such as an undo, SHALL keep its 10-second display time; the snacks behind it wait for it.

#### Scenario: A second snack waits
- **WHEN** a snack is visible and a second snack is published
- **THEN** the second snack SHALL appear only after the first has been dismissed and its exit motion has ended
- **AND** at no moment SHALL two snacks be visible

#### Scenario: Waiting snacks keep their order
- **WHEN** three snacks are published within one second
- **THEN** they SHALL appear one after another in the order they were published

#### Scenario: An undo window is kept
- **WHEN** a fan unfollows an artist and, while its undo snack is visible, changes the hype level of another artist
- **THEN** the undo snack SHALL stay for its full display time, with its undo action available
- **AND** the hype snack SHALL appear after it

#### Scenario: Replacing an earlier snack
- **WHEN** a screen shows a snack for an artist and then publishes a new snack that replaces its earlier snack for the same artist
- **THEN** the earlier snack SHALL be dismissed and the new snack SHALL appear next, before any other waiting snack
- **AND** only one snack SHALL be shown for that artist

#### Scenario: Dismissing a waiting snack
- **WHEN** a caller invokes `snack.handle.dismiss()` on a snack that is still waiting
- **THEN** the snack SHALL be removed from the wait and SHALL never appear
- **AND** its `onDismiss` callback SHALL fire exactly once

#### Scenario: The update snack gives way
- **WHEN** the app update snack is visible and a follow publishes a snack
- **THEN** the update snack SHALL leave, the follow snack SHALL appear, and the update snack SHALL appear again after the follow snack has left
- **AND** the update SHALL NOT be applied or lost


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

## REMOVED Requirements

### Requirement: At most three snacks are shown at once
**Reason**: Material 3 shows one snackbar at a time ("Only one snackbar may be displayed at a time"; "Don't stack snackbars on top of one another", m3.material.io snackbar guidelines). Stacked snacks also overlapped, because each is its own top-layer element.
**Migration**: "Snacks appear one at a time" replaces it; its undo-window and replacement scenarios carry over.
