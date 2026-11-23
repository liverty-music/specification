## ADDED Requirements

### Requirement: A snack waits while the fan is reading or using it

The display time of a snack SHALL NOT run while the fan holds a pointer over the snack or while keyboard focus is inside it, and SHALL start again from the remaining time when the pointer leaves or focus moves out. A snack the fan has not touched keeps the display times stated in "Snack Bar Component". Under reduced motion this is unchanged.

#### Scenario: Pointer over a snack with an action

- **WHEN** a snack with an action has been shown for 6 seconds and the fan moves a pointer over it
- **THEN** the snack stays shown for as long as the pointer is over it
- **AND** when the pointer leaves, the snack hides after the 4 seconds that were left

#### Scenario: Focus inside a snack

- **WHEN** the fan moves keyboard focus onto the action of a snack
- **THEN** the snack is not hidden while the focus is there
