### Requirement: Persistent elements use Popover API for Top Layer promotion

The application SHALL use `popover="manual"` to promote persistent non-modal elements to the Top Layer, replacing z-index-based stacking. Zero z-index declarations SHALL remain in the codebase.

#### Scenario: Bottom navigation bar uses popover for Top Layer promotion
- **WHEN** the bottom navigation bar component attaches
- **THEN** it SHALL use `popover="manual"` attribute and call `showPopover()` on attached
- **AND** the `z-30` Tailwind class SHALL be removed
- **AND** the nav bar SHALL paint above all non-Top-Layer content without z-index
- **AND** Top Layer dialogs (via `showModal()`) SHALL naturally paint above the nav bar due to later insertion order

#### Scenario: Toast notification uses popover for Top Layer promotion
- **WHEN** a toast notification is displayed
- **THEN** it SHALL use `popover="manual"` attribute and call `showPopover()` when shown
- **AND** the `z-50` Tailwind class SHALL be removed
- **AND** `pointer-events: none` SHALL remain on the container with `pointer-events: auto` on individual toast items
- **AND** toast SHALL call `hidePopover()` + `showPopover()` to re-insert at the top of the Top Layer stack when a dialog is already open

#### Scenario: Coach mark uses popover for Top Layer promotion
- **WHEN** an onboarding coach mark is activated
- **THEN** it SHALL use `popover="manual"` attribute and call `showPopover()` on activation
- **AND** `z-index: 9999` SHALL be removed from `coach-mark.css`
- **AND** `pointer-events: none` SHALL be applied to the overlay canvas with `pointer-events: auto` on dismiss/next buttons
- **AND** click-through to the spotlighted element SHALL be handled by forwarding pointer events from the transparent canvas region via `elementFromPoint()` delegation
- **AND** the tooltip SHALL use CSS Anchor Positioning (`position-anchor`, `position-area`) instead of `getBoundingClientRect()` JS calculations
