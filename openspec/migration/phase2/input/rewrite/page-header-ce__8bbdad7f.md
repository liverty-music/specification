<!-- spec: page-header-ce | target: components/infrastructure/fan/web/global/page-header | flags: CLASSNAME | new_name: Page header is globally registered -->

### Requirement: Page header is globally registered
The `PageHeader` class SHALL be registered globally in `main.ts` so all routes can use `<page-header>` without per-route `<import>` statements.

#### Scenario: Usage without explicit import
- **WHEN** a route template uses `<page-header title-key="...">` without an `<import>` tag
- **THEN** the component resolves and renders correctly
