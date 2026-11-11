## MODIFIED Requirements

### Requirement: Page header provides consistent visual styling
The `page-header` CE SHALL encapsulate the shared header styles: padding, bottom border, background color, and `<h1>` typography (font-family, size, weight, letter-spacing).

#### Scenario: Visual consistency across routes
- **WHEN** `page-header` is rendered in my-artists, settings, and tickets routes
- **THEN** all three headers share identical padding (12 px), border (`1px solid` at 10% white), background (a gradient from the `surface-container` color role on the left to the brand primary at 8% opacity on the right), and `<h1>` typography (the headline-small style)
