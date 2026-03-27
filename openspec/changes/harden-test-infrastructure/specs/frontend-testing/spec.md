## MODIFIED Requirements

### Requirement: Test infrastructure provides shared mock factories
The test suite SHALL provide reusable mock factories for commonly used DI dependencies (`ILogger`, `IAuthService`, `IRouter`, RPC service clients) in `test/helpers/`.

#### Scenario: Creating a mock logger
- **WHEN** a test imports `createMockLogger` from `test/helpers/mock-logger`
- **THEN** it SHALL return an object implementing `ILogger` with all methods as Vitest spies (`debug`, `info`, `warn`, `error`, `scopeTo`)

#### Scenario: Creating a mock auth service
- **WHEN** a test imports `createMockAuth` from `test/helpers/mock-auth`
- **THEN** it SHALL return an object implementing `IAuthService` with configurable `isAuthenticated`, `user`, and spy methods for `signIn`, `signOut`, `signUp`, `handleCallback`

#### Scenario: Creating a test DI container
- **WHEN** a test calls `createTestContainer` with mock registrations
- **THEN** it SHALL return an Aurelia `IContainer` with the provided mocks registered and `ILogger` pre-registered

#### Scenario: Creating a composition fixture helper
- **WHEN** a test calls `createCompositionFixture` with a parent CE, child CE deps, and mock services
- **THEN** it SHALL return a `createFixture` instance with all CEs registered and services mocked via `Registration.instance()`

## ADDED Requirements

### Requirement: Vitest environment is managed by vitest, not manually
The `test/setup.ts` file SHALL NOT create its own JSDOM instance. Vitest's `environment: 'jsdom'` (configured in `vitest.config.ts`) SHALL be the single source of truth for the DOM environment.

#### Scenario: setup.ts does not import jsdom
- **WHEN** `test/setup.ts` is loaded
- **THEN** it SHALL NOT import from `jsdom` package
- **AND** it SHALL NOT call `new JSDOM()`
- **AND** it SHALL NOT assign to `globalThis.window`, `globalThis.document`, or `globalThis.navigator`

#### Scenario: setup.ts initializes only Aurelia platform bridge
- **WHEN** `test/setup.ts` is loaded
- **THEN** it SHALL call `new BrowserPlatform(window)` using vitest's environment-provided `window`
- **AND** it SHALL call `setPlatform()` and `BrowserPlatform.set()` per [Aurelia testing docs](https://docs.aurelia.io/developer-guides/overview)

#### Scenario: Fixture cleanup uses vitest-managed environment
- **WHEN** a test that created fixtures completes
- **THEN** fixture `stop(true)` SHALL execute while vitest's jsdom is still active (no stale `document` reference)

### Requirement: Aurelia template module graph is contained in tests
Test files SHALL NOT trigger recursive Aurelia template resolution chains that load untested component dependencies.

#### Scenario: Direct CE import for component tests
- **WHEN** a test targets a specific custom element (e.g., `ConcertHighway`)
- **THEN** the test SHALL import the CE class directly from its source file (e.g., `src/components/live-highway/concert-highway`)
- **AND** it SHALL NOT import via a parent route module that would trigger template chain resolution

#### Scenario: HTML template mock for route-level tests
- **WHEN** a test targets a route component's ViewModel logic (e.g., `DashboardRoute`)
- **THEN** the test SHALL mock the route's HTML template via `vi.mock('...route.html', () => ({ default: '<minimal-template>' }))` per [Vitest module mocking docs](https://vitest.dev/guide/mocking.html)
- **AND** the mock template SHALL NOT contain `<import from="...">` directives

#### Scenario: No cascading document reference errors
- **WHEN** any test file is executed by vitest
- **THEN** it SHALL NOT produce `ReferenceError: document is not defined` from transitive Aurelia template imports

### Requirement: CE composition integration tests verify layout propagation
Integration tests SHALL verify that custom elements render with correct layout when composed inside parent containers, using `createFixture` from `@aurelia/testing` per [Aurelia Testing Components docs](https://docs.aurelia.io/developer-guides/overview/testing-components).

#### Scenario: ConcertHighway renders with non-zero height in grid parent
- **WHEN** `ConcertHighway` is rendered via `createFixture` inside a CSS Grid container with `dateGroups` bound
- **THEN** the `concert-highway` element SHALL be present in the DOM
- **AND** it SHALL contain date separator elements and lane grid elements matching the provided dateGroups

#### Scenario: ConcertHighway with EventCard child CEs
- **WHEN** `ConcertHighway` is rendered with `EventCard` registered as a dependency
- **THEN** `event-card` elements SHALL be present in the DOM for each event in the dateGroups

#### Scenario: ConcertHighway in readonly mode
- **WHEN** `ConcertHighway` is rendered with `is-readonly="true"`
- **THEN** clicking an `event-card` SHALL NOT dispatch an `event-selected` custom event

#### Scenario: ConcertHighway beam index map
- **WHEN** `ConcertHighway` is rendered with dateGroups containing events where `matched` is `true`
- **THEN** `component.beamIndexMap` SHALL contain entries mapping each matched event ID to a beam index

### Requirement: Dashboard-route has integration tests
The `DashboardRoute` component SHALL have `createFixture`-based integration tests verifying state management and service interaction.

#### Scenario: Loading state on initial render
- **WHEN** `DashboardRoute` is rendered via `createFixture` with mocked services
- **THEN** the `loadData()` method SHALL call `concertService.listWithProximity`

#### Scenario: Error state when service fails
- **WHEN** the concert service rejects with an error
- **THEN** `loadError` SHALL be truthy
- **AND** the template SHALL render the error state (not the concert highway)

#### Scenario: Empty state when no concerts exist
- **WHEN** the concert service resolves with zero groups
- **THEN** `dateGroups` SHALL be empty
- **AND** the template SHALL render the empty state placeholder

#### Scenario: Concert data populates dateGroups
- **WHEN** the concert service resolves with proximity groups
- **THEN** `dateGroups` SHALL contain the mapped groups
- **AND** the template SHALL render the concert highway (not loading or error state)

#### Scenario: needsRegion blurs concert highway
- **WHEN** no home region is set (needsRegion is true)
- **THEN** the concert-highway element SHALL have `data-blurred="true"`

### Requirement: Per-file vitest environment annotations optimize execution
Test files that do not require DOM access SHALL declare `// @vitest-environment node` to skip jsdom initialization per [Vitest environment docs](https://vitest.dev/guide/environment.html#environments-for-specific-files).

#### Scenario: Mapper tests run in node environment
- **WHEN** a mapper test file (e.g., `test/adapter/rpc/mapper/artist-mapper.spec.ts`) is executed
- **THEN** it SHALL contain `// @vitest-environment node` at the top
- **AND** it SHALL execute without jsdom overhead

#### Scenario: Entity tests run in node environment
- **WHEN** an entity test file (e.g., `src/entities/artist.spec.ts`) is executed
- **THEN** it SHALL contain `// @vitest-environment node` at the top

#### Scenario: Service tests without DOM dependency run in node environment
- **WHEN** a service test that only tests pure logic (no DOM, no Aurelia lifecycle) is executed
- **THEN** it SHALL contain `// @vitest-environment node` at the top

#### Scenario: Component and route tests remain in jsdom environment
- **WHEN** a test file uses `createFixture`, `BrowserPlatform`, or DOM APIs
- **THEN** it SHALL NOT declare `// @vitest-environment node` (inherits jsdom from config)
