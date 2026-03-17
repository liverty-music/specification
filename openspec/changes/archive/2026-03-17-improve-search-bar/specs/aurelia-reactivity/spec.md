## ADDED Requirements

### Requirement: Collection observation via native Set binding
Template bindings that need to observe membership in a `Set` SHALL bind directly to `Set.has()` instead of delegating through view model methods, to leverage Aurelia 2's native collection observation.

#### Scenario: Template binding observes Set.has() reactively
- **WHEN** a template expression uses `someSet.has(value)` in a binding
- **AND** `someSet.add(value)` or `someSet.delete(value)` is called
- **THEN** the binding SHALL re-evaluate and the DOM SHALL update to reflect the new membership state

#### Scenario: View model exposes Set via getter for template consumption
- **WHEN** a service owns a `Set` that must be observed in a template
- **THEN** the view model SHALL expose it via a `public get` accessor returning `ReadonlySet<T>`
- **AND** the template SHALL bind to `getter.has(value)` directly
- **AND** the view model SHALL NOT maintain a copy of the Set for reactivity purposes

#### Scenario: Method calls wrapping Set.has() are not reactive
- **WHEN** a template expression calls a view model method (e.g., `isItemSelected(id)`) that internally calls `this.someSet.has(id)`
- **THEN** Aurelia SHALL NOT automatically track the Set dependency inside the method
- **AND** the binding SHALL NOT re-evaluate when the Set contents change
- **AND** this pattern SHALL be avoided in favor of direct `Set.has()` binding
