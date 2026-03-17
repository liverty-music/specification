## ADDED Requirements

### Requirement: Semantic HTML element usage

All interactive overlays (popovers, modals, prompts) SHALL use native `<dialog>` elements instead of `<div>` with `popover` attribute.

Action button groups within dialogs and cards SHALL be wrapped in `<footer>` elements.

Content containers SHALL use the most specific semantic HTML element available (`<section>`, `<article>`, `<figure>`, `<header>`, `<fieldset>`, `<output>`) instead of generic `<div>`.

Loading/status indicators SHALL use `<output role="status">` instead of `<div role="status">`.

#### Scenario: Dialog elements for overlays
- **WHEN** a component renders an overlay (popover, modal, prompt)
- **THEN** the overlay root element MUST be a `<dialog>` element

#### Scenario: Footer for action groups
- **WHEN** a dialog or card contains action buttons
- **THEN** the button group MUST be wrapped in a `<footer>` element

#### Scenario: No unnecessary div wrappers
- **WHEN** a `<div>` is used purely as a content wrapper without layout purpose
- **THEN** it MUST be replaced with the appropriate semantic element or removed entirely

### Requirement: Minimal div nesting depth

Template nesting depth of `<div>` elements SHALL NOT exceed 2 levels within any component.

Wrapper `<div>` elements that serve no layout or semantic purpose SHALL be removed.

#### Scenario: Nesting depth check
- **WHEN** a component template is rendered
- **THEN** the maximum depth of nested `<div>` elements MUST NOT exceed 2 levels
