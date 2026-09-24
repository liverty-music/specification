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
