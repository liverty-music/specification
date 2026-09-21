<!-- spec: page-header-ce | target: components/infrastructure/fan/web/global/page-header | flags: CLASSNAME | new_name: Page header is globally registered -->

### Requirement: Page header is globally registered
The `<page-header>` custom element SHALL be registered globally so all routes can use it without per-route `<import>` statements.

#### Scenario: Usage without explicit import
- **WHEN** a route template uses `<page-header title-key="...">` without an `<import>` tag
- **THEN** the component resolves and renders correctly
