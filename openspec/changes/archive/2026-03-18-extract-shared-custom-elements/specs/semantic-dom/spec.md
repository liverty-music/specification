## ADDED Requirements

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

### Requirement: Prompt consolidation to toast CE
All top-positioned user-action prompts SHALL use `<toast>` as their presentation primitive.

#### Scenario: Existing prompt components migrated
- **WHEN** notification-prompt or pwa-install-prompt renders a permission/install banner
- **THEN** the banner SHALL be rendered via `<toast open.bind="...">` with slotted content
- **AND** the component SHALL NOT contain its own popover positioning or banner CSS
