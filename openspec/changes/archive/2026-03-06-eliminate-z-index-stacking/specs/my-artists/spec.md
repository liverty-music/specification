### Requirement: Context menu uses native dialog

The grid view context menu (long-press on artist tile) SHALL use the native `<dialog>` element with `showModal()` for Top Layer promotion.

#### Scenario: Long-press opens context menu dialog
- **GIVEN** the Grid view is active
- **WHEN** the user long-presses a tile
- **THEN** a `<dialog>` SHALL open via `showModal()` with passion level options and an unfollow action
- **AND** the dialog SHALL NOT use z-index utilities
- **AND** the `::backdrop` pseudo-element SHALL dim the page

#### Scenario: Context menu dismissal
- **WHEN** the user taps the backdrop or presses ESC
- **THEN** the context menu dialog SHALL close via `dialogElement.close()`

#### Scenario: Context menu slide-up animation
- **WHEN** the context menu dialog opens
- **THEN** it SHALL animate from the bottom of the viewport using `@starting-style` (300ms ease-out)

### Requirement: Passion explanation modal uses native dialog

The passion level explanation modal (displayed during tutorial) SHALL use the native `<dialog>` element with `showModal()`.

#### Scenario: Tutorial displays passion explanation
- **WHEN** the tutorial triggers the passion explanation step
- **THEN** a `<dialog>` SHALL open via `showModal()` with a centered explanation card
- **AND** the dialog SHALL NOT use z-index utilities
- **AND** the `::backdrop` SHALL dim the page with `oklch(0% 0 0 / 0.7)` opacity

#### Scenario: Passion explanation is non-dismissible during tutorial
- **WHEN** the passion explanation dialog is open during the tutorial
- **THEN** the `cancel` event SHALL be suppressed (no ESC dismissal)
- **AND** no close button or backdrop-click-to-close SHALL be provided
- **AND** the dialog SHALL be closed programmatically when the tutorial step completes
