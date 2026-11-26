## ADDED Requirements

### Requirement: The launcher grows in

The launcher (the FAB) SHALL grow from nothing when it first shows (the screen's launcher appears, or edit mode ends), on the spatial spring it already uses to sink, instead of appearing at once. It SHALL NOT shrink or grow again when the arc opens, and it keeps its place above the arc's scrim. Under reduced motion it fades in over at most 100 ms, without growing. While a tab switches, the launcher stays in its place and does not fade.

#### Scenario: Edit mode ends

- **WHEN** the fan leaves edit mode and the launcher shows again
- **THEN** the launcher grows from nothing to its size on the spatial spring

#### Scenario: The launcher stays whole and on top while the arc opens

- **WHEN** the fan taps the launcher and the arc opens
- **THEN** the launcher keeps its size through the whole opening and is the topmost element at its own centre, above the arc's scrim

### Requirement: The launcher is an accessible disclosure that keeps focus

The action menu SHALL be an accessible disclosure control, not an ARIA menu: it SHALL expose
its expanded/collapsed state and reference the panel it controls. When the panel
opens, keyboard focus SHALL stay on the action menu, which is then the close control,
and the panel's items SHALL come next in the focus order (M3 FAB menu: focus stays on
the close button; the disclosure pattern keeps focus on its button); when it closes,
focus SHALL return to the action menu. The panel SHALL be dismissible by pressing Escape and by activating
outside it (light dismiss).

#### Scenario: action menu exposes disclosure state

- **WHEN** the action menu is rendered
- **THEN** it SHALL expose an expanded/collapsed state to assistive technology
- **AND** it SHALL reference the panel element it controls
- **AND** it SHALL NOT be exposed as an ARIA `menu` with `menuitem` children

#### Scenario: Focus stays on the action menu, and Tab reaches the panel

- **WHEN** the user opens the launcher from the keyboard
- **THEN** keyboard focus SHALL stay on the action menu
- **AND** pressing Tab SHALL move focus to the panel's first item
- **WHEN** the user closes the launcher
- **THEN** focus SHALL return to the action menu

#### Scenario: Escape and outside activation dismiss the panel

- **WHEN** the panel is open and the user presses Escape or activates outside the panel
- **THEN** the panel SHALL close

## REMOVED Requirements

### Requirement: Launcher accessibility contract

**Reason**: When the panel opens, focus now stays on the action menu (the close control) instead of moving to the panel's first item, so the requirement and its scenario "Focus moves into the panel and back" no longer hold.
**Migration**: "The launcher is an accessible disclosure that keeps focus" holds the same contract and scenarios, with that one replaced by "Focus stays on the action menu, and Tab reaches the panel".
