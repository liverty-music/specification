### Requirement: Retained z-index exceptions

The application SHALL retain z-index on specific elements where the native `<dialog>` Top Layer is not an appropriate replacement. Each retained z-index usage SHALL have documented rationale.

#### Scenario: Bottom navigation bar retains z-30
- **WHEN** the bottom navigation bar renders
- **THEN** it SHALL use `z-30` to sit above scrolling page content
- **AND** this is retained because the nav bar is a persistent fixed element with no `<dialog>` equivalent
- **AND** Top Layer dialogs (via `showModal()`) naturally paint above the nav bar without z-index conflicts
- **AND** `::backdrop` pseudo-elements dim the nav bar correctly when a dialog is open

#### Scenario: Coach mark retains z-9999
- **WHEN** an onboarding coach mark is active
- **THEN** it SHALL use `z-9999` to paint above all non-Top-Layer elements including the nav bar
- **AND** this is retained because the coach mark is a non-modal spotlight overlay that must allow click-through on the highlighted element
- **AND** `<dialog>` is not suitable because it would trap focus and block click-through interaction on the spotlight area
