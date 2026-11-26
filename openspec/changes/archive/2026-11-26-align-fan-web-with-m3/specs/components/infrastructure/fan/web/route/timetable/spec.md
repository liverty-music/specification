## ADDED Requirements

### Requirement: The month-jump capsule fades in and out

The month-jump capsule SHALL fade in when it appears (the list is first scrolled or a jump is made) and fade out when it goes (the FAB's action list opens, or no month is left to jump to), over the `md.sys.spring.effects` duration (200 ms) with the effects spring's curve, instead of appearing and vanishing at once. Under reduced motion it fades over at most 100 ms.

#### Scenario: The capsule gives way to the FAB with a fade

- **WHEN** the capsule is showing and the FAB's action list opens
- **THEN** the capsule fades out over 200 ms and is then no longer rendered
- **AND** when the list closes it fades back in
