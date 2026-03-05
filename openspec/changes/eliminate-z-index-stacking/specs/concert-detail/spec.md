### Requirement: Event detail bottom sheet uses native dialog

The event detail bottom sheet SHALL use the native `<dialog>` element with `showModal()` for Top Layer promotion, instead of fixed-position `<div>` elements with z-index utilities.

#### Scenario: Open detail from dashboard
- **WHEN** a user taps a concert card on the dashboard
- **THEN** the system SHALL open a `<dialog>` element via `showModal()`
- **AND** the dialog SHALL be promoted to the browser's Top Layer
- **AND** the `::backdrop` pseudo-element SHALL dim the page including the navigation bar
- **AND** the dialog SHALL NOT use z-index utilities (`z-40`, `z-50`, or any `z-*` class)

#### Scenario: Slide-up animation
- **WHEN** the event detail dialog opens
- **THEN** the dialog SHALL animate from `translateY(100%)` to `translateY(0)` with `opacity: 0` to `opacity: 1`
- **AND** the animation SHALL use `@starting-style` for the entry transition (300ms ease-out)
- **AND** the `::backdrop` SHALL fade in over the same duration

#### Scenario: Dismiss via backdrop
- **WHEN** the user taps the `::backdrop` area (outside the sheet content)
- **THEN** the sheet SHALL close via `dialogElement.close()`
- **AND** the URL SHALL revert to the dashboard URL

#### Scenario: Dismiss via swipe-down
- **WHEN** the user swipes down on the sheet content
- **THEN** the sheet SHALL follow the touch gesture and dismiss when the drag exceeds the threshold
- **AND** swipe-to-dismiss SHALL be suppressed during the onboarding DETAIL step (`isDismissBlocked`)

#### Scenario: ESC key behavior during onboarding
- **WHEN** the user presses ESC while the detail sheet is open during the onboarding DETAIL step
- **THEN** the `cancel` event SHALL be suppressed and the dialog SHALL remain open
