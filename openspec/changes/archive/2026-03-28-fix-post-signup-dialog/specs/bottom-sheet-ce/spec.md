## MODIFIED Requirements

### Requirement: Bottom Sheet Custom Element
The system SHALL provide a `<bottom-sheet>` custom element as the single dialog primitive for all overlay content, using the Popover API with CSS scroll-snap dismiss.

#### Scenario: Basic open/close via bindable
- **WHEN** `<bottom-sheet open.bind="isOpen">` has `open` set to `true`
- **THEN** the CE SHALL call `showPopover()` on the CE host element (via `resolve(INode)`)
- **AND** the sheet-body SHALL be visible at the bottom of the viewport via CSS `initial-snap` animation (no JS `scrollTo` required)
- **WHEN** `open` is set to `false`
- **THEN** the CE SHALL call `hidePopover()` on the CE host element and the sheet SHALL animate out

#### Scenario: Open bound to true at component creation time
- **WHEN** `open` is bound to `true` at initial bind time (before `attached()`)
- **AND** `openChanged(true)` is called during the `binding` phase
- **THEN** `showPopover()` SHALL be called but MAY fail silently if the `popover` attribute is not yet set
- **AND** the error SHALL be caught and suppressed (matching the existing `hidePopover()` try-catch pattern)
- **AND** the `attached()` lifecycle hook SHALL retry via `if (this.open) this.openChanged(true)` after the `popover` attribute is initialized
- **AND** the sheet SHALL open successfully at `attached()` time
