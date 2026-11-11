## ADDED Requirements

### Requirement: A snackbar clears a floating button

On a screen where a button floats over the bottom of the window, such as the extended action button of the concerts list, the snackbar SHALL sit above that button and SHALL NOT cover it.

#### Scenario: A snack does not cover the floating button

- **WHEN** a snackbar appears on the concerts list on a 390 px wide phone, where the extended action button floats at the bottom
- **THEN** the snackbar's bottom edge is above the button's top edge
