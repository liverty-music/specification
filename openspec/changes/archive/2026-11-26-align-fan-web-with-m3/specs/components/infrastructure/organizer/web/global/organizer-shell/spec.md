## ADDED Requirements

### Requirement: The console's menus fade in and out

The menus of the console (the account menu, the artist menu and the overflow menu of a list), which share one menu style, SHALL fade in when they open and fade out when they close, over the `md.sys.spring.effects` duration (200 ms) with the effects spring's curve, instead of appearing and vanishing at once. Under reduced motion they fade over at most 100 ms.

#### Scenario: Opening and closing the account menu

- **WHEN** the person opens the account menu and then closes it
- **THEN** the menu fades in over 200 ms and, on closing, fades out and is then not rendered
