# Toast

## Purpose

Provides transient toast notifications that surface live-event updates and background-operation failures, reverting any optimistic UI change when an action fails.

## Requirements

### Requirement: Dynamic Toast Notifications for Live Events
The system SHALL provide instant feedback about available live events using dynamic toast notifications.

#### Scenario: Live event notification on artist follow
- **WHEN** a user taps an artist bubble
- **AND** the artist has upcoming live events in the database
- **THEN** the system SHALL display a dynamic toast notification from the top of the screen
- **AND** the toast SHALL show the message: "🎫 [Artist Name] has upcoming live events!"
- **AND** the toast SHALL remain visible for 2-3 seconds
- **AND** the toast SHALL fade out smoothly

#### Scenario: No notification for artists without events
- **WHEN** a user taps an artist bubble
- **AND** the artist has no upcoming live events in the database
- **THEN** the system SHALL NOT display a toast notification
- **AND** the bubble absorption animation SHALL proceed normally

---

### Requirement: Fire-and-forget failures show a toast and revert optimistic UI
The system SHALL replace silent error swallowing in services with explicit error states that callers can distinguish from empty-data states.

#### Scenario: Service method returns error result instead of empty fallback
- **WHEN** a service method fails to fetch data from the backend
- **THEN** the method SHALL throw the error to the caller (not silently return an empty array or false)
- **AND** the caller SHALL handle the error via `promise.bind` catch block or explicit try/catch with user feedback

#### Scenario: Fire-and-forget operations provide user feedback on failure
- **WHEN** a fire-and-forget RPC operation (e.g., artist follow) fails
- **THEN** the system SHALL display a toast notification informing the user of the failure
- **AND** the system SHALL revert any optimistic UI updates

### Requirement: Toast notification service manages toast lifecycle
The `ToastNotification.show` method SHALL add a toast, animate it visible, auto-dismiss after the specified duration, and remove it after the exit animation.

#### Scenario: Show a toast
- **WHEN** `show` is called with a message
- **THEN** a toast item SHALL be added to `toasts` array and become `visible` after the next animation frame

#### Scenario: Auto-dismiss after duration
- **WHEN** `durationMs` elapses after showing a toast
- **THEN** the toast `visible` SHALL be set to `false`

#### Scenario: Remove after exit animation
- **WHEN** 400ms elapses after a toast is dismissed
- **THEN** the toast SHALL be removed from the `toasts` array

### Requirement: Toast custom element as a top-positioned popover banner
The system SHALL provide a `<toast>` custom element as a top-positioned popover banner for user-action prompts (notification permission, PWA install).

#### Scenario: Basic open/close via bindable
- **WHEN** `<toast open.bind="isVisible">` has `open` set to `true`
- **THEN** the CE SHALL call `showPopover()` on the internal `<dialog popover="manual">`
- **AND** the banner SHALL appear at the top of the viewport with slide-down animation
- **WHEN** `open` is set to `false`
- **THEN** the CE SHALL call `hidePopover()`

#### Scenario: Fixed top positioning
- **WHEN** the toast is open
- **THEN** the element SHALL be positioned at `inset-block-start: 0` with `inset-inline: 1rem`
- **AND** background SHALL be `var(--color-surface-raised)`
- **AND** border SHALL be `1px solid var(--color-border-subtle)`
- **AND** border-radius SHALL be `var(--radius-card)`
- **AND** box-shadow SHALL be `var(--shadow-card-glow)`

#### Scenario: Slotted content
- **WHEN** content is placed inside `<toast>`
- **THEN** it SHALL be projected via `<au-slot>` into the popover body
- **AND** consuming components SHALL provide their own icon, title, description, and action buttons

#### Scenario: Non-modal overlay
- **WHEN** the toast is displayed
- **THEN** it SHALL use `popover="manual"` (no light dismiss)
- **AND** background content SHALL remain interactive (not inert)

#### Scenario: Entry/exit animation
- **WHEN** the toast opens
- **THEN** it SHALL animate via `@starting-style` from `opacity: 0; translate: 0 -1rem` to `opacity: 1; translate: 0 0`
- **WHEN** the toast closes
- **THEN** it SHALL transition to `opacity: 0; translate: 0 -1rem`
- **AND** `display` and `overlay` transitions SHALL use `allow-discrete`

#### Scenario: Toast closed event
- **WHEN** the toast is closed
- **THEN** the CE SHALL dispatch a `toast-closed` CustomEvent with `bubbles: true`
