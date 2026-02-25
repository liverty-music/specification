## Why

The frontend codebase uses Aurelia 2 but does not leverage many of its most powerful features introduced through Beta 24-27. An audit revealed zero usage of `@watch`, `@computed`, `batch()`, value converters, and binding behaviors (including built-in `debounce`/`throttle`). All `repeat.for` loops lack `key.bind`, causing potential DOM reconciliation issues. The CSS layer relies solely on Tailwind utilities without using modern CSS capabilities (Container Queries, View Transitions API, `:has()` selectors) that the web-app-specialist guidelines mandate.

## What Changes

- Add `key.bind` to all `repeat.for` loops across the application for correct list reconciliation
- Introduce `@watch` and `@computed` decorators to replace manual event wiring and optimize getter evaluation
- Use `batch()` for multi-property state updates that currently trigger multiple DOM update cycles
- Add `& debounce` and `& throttle` binding behaviors to search inputs and touch/swipe handlers
- Replace chained `if.bind` patterns with `switch.bind` for multi-branch conditionals
- Use `show.bind` for frequently toggled UI elements (bottom nav bar, loading states)
- Adopt `.class` binding syntax instead of string interpolation for class toggling
- Create reusable value converters for date/time formatting
- Adopt Container Queries for component-level responsive design in event card layouts
- Adopt View Transitions API for route change animations (replacing CSS animation on `au-viewport > *`)
- Add route `title` properties for document title management

## Capabilities

### New Capabilities
- `aurelia-reactivity`: Covers adoption of `@watch`, `@computed`, `batch()`, and `@observable` patterns across components and services for fine-grained reactivity
- `aurelia-template-optimization`: Covers `key.bind`, `switch.bind`, `show.bind`, `.class` binding, binding behaviors (`debounce`, `throttle`), and value converters
- `modern-css-platform`: Covers Container Queries, View Transitions API, `:has()` selectors, and CSS Logical Properties adoption

### Modified Capabilities
- `design-system`: Adding Container Queries and View Transitions API to the design token system; updating animation requirements from CSS keyframes to View Transitions

## Impact

- **Frontend repo** (`liverty-music/frontend`): All component templates, service classes, and CSS files
- **No API/backend changes**: This is a pure frontend refactoring
- **No breaking changes**: All modifications are internal implementation improvements
- **Dependencies**: No new npm packages required (all features are built into Aurelia 2 and the CSS platform)
- **Testing**: Existing tests continue to pass; component render tests should be added using `createFixture`
