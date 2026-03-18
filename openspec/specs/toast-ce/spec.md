# Toast Custom Element

## Purpose

Provides a `<toast>` custom element as a top-positioned popover banner for user-action prompts (notification permission, PWA install).

## Requirements

### Requirement: Toast Custom Element
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
