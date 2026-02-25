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

#### Scenario: Computed getter with explicit dependencies
- **WHEN** a getter derives its value from multiple observable properties
- **THEN** the getter SHALL be decorated with `@computed` listing its dependency property names
- **AND** the getter SHALL only re-evaluate when one of the listed dependencies changes

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
