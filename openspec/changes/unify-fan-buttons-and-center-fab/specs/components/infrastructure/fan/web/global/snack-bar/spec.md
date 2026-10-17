## ADDED Requirements

### Requirement: Snack bars sit directly above the bottom navigation

Every snack bar, whatever its severity or sender, SHALL be placed at the bottom of the screen with its bottom edge one `space-s` step above the top of the bottom navigation bar and the bottom safe-area inset. While a persistent bottom banner (the signup prompt or the install banner) is visible above the navigation bar, the snack bar SHALL sit that same step above the banner instead, using the banner's rendered height; a banner that is not visible SHALL add no height.

#### Scenario: No banner is visible
- **WHEN** a snack bar opens and no persistent bottom banner is visible
- **THEN** the gap between the snack bar's bottom edge and the navigation bar's top edge SHALL be one `space-s` step (16 to 20px)

#### Scenario: Install banner dismissed
- **WHEN** the fan has dismissed the install banner, so that it is no longer visible
- **AND** a snack bar opens
- **THEN** the snack bar SHALL sit one `space-s` step above the navigation bar, not above the space the banner used to occupy

#### Scenario: A banner is visible
- **WHEN** a snack bar opens while the signup prompt or the install banner is visible
- **THEN** the snack bar's bottom edge SHALL sit one `space-s` step above the banner's top edge
- **AND** the snack bar SHALL NOT cover any part of the banner

#### Scenario: Same placement for every severity
- **WHEN** an info, warning and error snack bar are each shown in turn under the same conditions
- **THEN** all three SHALL occupy the same vertical position

### Requirement: The update action stands out as a button on the snack bar

When the update snack is displayed, its action button (labelled with `pwa.updateAction`) SHALL be visually distinguished from the snack body text so that users immediately identify it as a button. The button SHALL use the on-container button style (see UI Primitives): a translucent white fill, a white border and the shared button corner radius. When the update snack appears, the button SHALL glow three times and then stay still for as long as the snack is shown. The glow SHALL NOT play when `prefers-reduced-motion: reduce` is active. The snack's leading icon SHALL depict a refresh, not a ticket.

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

#### Scenario: Leading icon depicts a refresh
- **WHEN** the update snack is visible
- **THEN** its leading icon SHALL be a refresh icon

## MODIFIED Requirements

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
- **THEN** the snack SHALL rise into place from below, animating from `opacity: 0; transform: translateY(1rem)` to `opacity: 1; transform: translateY(0)`
- **AND** the entry state SHALL be defined via `@starting-style` inside `:popover-open`

#### Scenario: CSS exit animation
- **WHEN** a snack popover is closed via `hidePopover()`
- **THEN** the snack SHALL sink out of place, animating from `opacity: 1; transform: translateY(0)` to `opacity: 0; transform: translateY(1rem)`
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

## REMOVED Requirements

### Requirement: The update action button is visually prominent
**Reason**: Its pill border with a continuous glow pulse was replaced by the shared on-container button style and a glow that plays three times. The shipped snack bar had already dropped the pill (frontend PR #603) without updating this requirement.
**Migration**: Replaced by "The update action stands out as a button on the snack bar". No data or setting is affected.
