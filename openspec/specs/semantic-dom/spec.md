# Semantic DOM

## Purpose

Defines the rules for semantic HTML element usage and minimal div nesting across all frontend components, ensuring accessible, meaningful markup and reduced DOM complexity.

## Requirements

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

---

### Requirement: Minimal div nesting depth

Template nesting depth of `<div>` elements SHALL NOT exceed 2 levels within any component.

Wrapper `<div>` elements that serve no layout or semantic purpose SHALL be removed.

#### Scenario: Nesting depth check
- **WHEN** a component template is rendered
- **THEN** the maximum depth of nested `<div>` elements MUST NOT exceed 2 levels

---

### Requirement: Dialog consolidation to bottom-sheet CE
All interactive overlay components SHALL use `<bottom-sheet>` as their dialog primitive instead of implementing custom `<dialog>` elements with duplicated CSS.

#### Scenario: Existing dialog components migrated
- **WHEN** event-detail-sheet, user-home-selector, hype-notification-dialog, error-banner, or any route-local dialog renders an overlay
- **THEN** the overlay SHALL be rendered via `<bottom-sheet open.bind="..." dismissable.bind="...">` with slotted content
- **AND** the component SHALL NOT contain its own dialog positioning, backdrop, handle-bar, or slide-in CSS

#### Scenario: Route-local dialogs eliminated
- **WHEN** settings-route renders the language selector or tickets-route renders QR/generating dialogs
- **THEN** these SHALL use `<bottom-sheet>` with slotted content
- **AND** the route CSS SHALL NOT contain dialog/modal/sheet CSS rules

---

### Requirement: Prompt consolidation to toast CE
All top-positioned user-action prompts SHALL use `<toast>` as their presentation primitive.

#### Scenario: Existing prompt components migrated
- **WHEN** notification-prompt or pwa-install-prompt renders a permission/install banner
- **THEN** the banner SHALL be rendered via `<toast open.bind="...">` with slotted content
- **AND** the component SHALL NOT contain its own popover positioning or banner CSS
