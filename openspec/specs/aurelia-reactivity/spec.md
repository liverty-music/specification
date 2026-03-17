# Aurelia Reactivity

## Purpose

Defines the reactive programming patterns for the Liverty Music frontend, ensuring efficient state observation, computed property caching, batched DOM updates, and observable side-effect handling using Aurelia 2's reactivity primitives.

## Requirements

### Requirement: Watch-based reactive observation
Components and services SHALL use the `@watch` decorator to observe cross-property and cross-service state changes instead of manual event subscriptions or polling.

#### Scenario: Component reacts to service state change
- **WHEN** a service singleton property (e.g., `DashboardService.selectedRegion`) changes
- **THEN** the component observing that property via `@watch` SHALL execute the decorated handler method
- **AND** the handler SHALL receive `(newValue, oldValue)` as arguments

#### Scenario: Multiple properties watched
- **WHEN** a component needs to react to changes in more than one property
- **THEN** each property SHALL have a separate `@watch` decorator on the handler method
- **AND** multiple `@watch` decorators MAY be stacked on the same handler if the reaction is identical

### Requirement: Computed property caching
Expensive getter computations referenced in templates SHALL use the `@computed` decorator to avoid unnecessary re-evaluation.

#### Scenario: Computed getter with automatic dependency tracking
- **WHEN** a getter derives its value from multiple observable properties
- **THEN** the getter SHALL be decorated with `@computed` to enable automatic dependency tracking
- **AND** the getter SHALL only re-evaluate when one of the accessed dependencies changes

#### Scenario: Simple getters remain undecorated
- **WHEN** a getter performs a trivial computation (e.g., string concatenation, boolean check)
- **THEN** the getter SHALL NOT be decorated with `@computed`
- **AND** Aurelia's default observation mechanism SHALL handle the binding

### Requirement: Batched multi-property updates
Service methods that mutate multiple observable properties in a single logical operation SHALL use `batch()` to coalesce DOM updates.

#### Scenario: Batch prevents intermediate renders
- **WHEN** a service method updates three or more properties that are template-bound
- **THEN** the mutations SHALL be wrapped in a `batch(() => { ... })` call
- **AND** the template SHALL update exactly once after the batch completes

#### Scenario: Optimistic UI updates excluded from batching
- **WHEN** a UI action requires immediate visual feedback (e.g., follow/unfollow toggle)
- **THEN** the optimistic property update SHALL NOT be wrapped in `batch()`
- **AND** the subsequent server confirmation/rollback MAY use `batch()` for the multi-property restore

### Requirement: Observable for side-effect properties
Properties whose changes require imperative side effects (e.g., error display, analytics) SHALL use the `@observable` decorator with a change handler.

#### Scenario: Observable triggers side effect
- **WHEN** a property decorated with `@observable` changes value
- **THEN** the corresponding `<propertyName>Changed(newValue, oldValue)` handler SHALL execute
- **AND** the handler SHALL perform only the side effect, not additional state mutations that could cascade

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
