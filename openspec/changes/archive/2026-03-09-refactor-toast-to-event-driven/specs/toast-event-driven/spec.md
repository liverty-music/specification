## ADDED Requirements

### Requirement: Typed toast event class
The system SHALL define a `Toast` event class with `message` (string), `severity` (ToastSeverity, default `'info'`), and `durationMs` (number, default `2500`) properties. This class SHALL be the sole mechanism for triggering toast notifications.

#### Scenario: Publishing a toast event
- **WHEN** any component calls `ea.publish(new Toast('message', 'error'))`
- **THEN** the `Toast` event is dispatched via `IEventAggregator` with the specified message and severity

#### Scenario: Default severity and duration
- **WHEN** a component calls `ea.publish(new Toast('message'))`
- **THEN** severity defaults to `'info'` and durationMs defaults to `2500`

### Requirement: Toast custom element subscribes to events
The `ToastNotification` custom element SHALL subscribe to `Toast` events via `IEventAggregator` during the `attaching` lifecycle hook and dispose the subscription during `detaching`.

#### Scenario: Event subscription lifecycle
- **WHEN** `<toast-notification>` attaches to the DOM
- **THEN** it subscribes to `Toast` events via `IEventAggregator`

#### Scenario: Event subscription cleanup
- **WHEN** `<toast-notification>` detaches from the DOM
- **THEN** the event subscription is disposed to prevent memory leaks

### Requirement: Toast rendering and auto-dismiss
The `ToastNotification` custom element SHALL display received toast messages using the Popover API and auto-dismiss them after the specified duration.

#### Scenario: Single toast display
- **WHEN** a `Toast` event is received
- **THEN** the toast message is rendered with the appropriate severity styling and a slide-in animation
- **THEN** the popover container is shown via `showPopover()`

#### Scenario: Auto-dismiss
- **WHEN** a toast's `durationMs` elapses
- **THEN** the toast slides out and is removed from the DOM
- **THEN** if no toasts remain, `hidePopover()` is called

#### Scenario: Multiple concurrent toasts
- **WHEN** multiple `Toast` events are received before prior toasts dismiss
- **THEN** all toasts are displayed simultaneously in a vertical stack

### Requirement: No DI service for toast
The system SHALL NOT register a DI singleton service for toast notifications. `IToastService` SHALL be removed. All toast triggering SHALL use `IEventAggregator.publish(new Toast(...))`.

#### Scenario: IToastService removal
- **WHEN** any component needs to show a toast
- **THEN** it resolves `IEventAggregator` (not `IToastService`) and publishes a `Toast` event
