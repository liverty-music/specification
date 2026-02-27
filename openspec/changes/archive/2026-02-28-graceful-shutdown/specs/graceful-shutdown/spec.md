## ADDED Requirements

### Requirement: Phased Shutdown Orchestration
The application SHALL execute shutdown in ordered phases: signal acknowledgment, request draining, async producer flushing, external client teardown, observability flushing, and data store closure. Each phase MUST complete or timeout before the next phase begins.

#### Scenario: Normal shutdown sequence
- **WHEN** the process receives SIGTERM
- **THEN** the shutdown manager executes phases in order: drain → flush → external → observe → datastore, and the process exits with code 0

#### Scenario: Phase timeout exceeded
- **WHEN** a shutdown phase exceeds the global shutdown deadline
- **THEN** the remaining phases are skipped, accumulated errors are logged, and the process exits

### Requirement: Health Check Shutdown State Transition
The health check handler SHALL immediately transition to `NOT_SERVING` status when SIGTERM is received, before the HTTP server begins its shutdown sequence.

#### Scenario: SIGTERM triggers health state change
- **WHEN** the process receives SIGTERM
- **THEN** the health check handler returns `NOT_SERVING` for all subsequent probe requests within 1ms of signal receipt

#### Scenario: In-flight requests unaffected by health transition
- **WHEN** the health check transitions to `NOT_SERVING` and in-flight RPC requests are still being processed
- **THEN** the in-flight requests complete normally via `http.Server.Shutdown()` connection draining

### Requirement: Background Goroutine Lifecycle Management
All background goroutines spawned during application initialization SHALL be tracked via `sync.WaitGroup` and awaited during the drain phase of shutdown.

#### Scenario: Cache cleanup goroutine completes before resource teardown
- **WHEN** shutdown begins and the cache cleanup goroutine is mid-execution
- **THEN** the drain phase waits for the goroutine to finish before proceeding to the flush phase

#### Scenario: Background goroutine respects cancellation
- **WHEN** the application context is cancelled
- **THEN** all tracked background goroutines exit within their next iteration cycle

### Requirement: Consumer Shutdown Context
The consumer application SHALL pass a fresh, non-cancelled context to its `Shutdown` method to ensure resource cleanup closers receive a valid context.

#### Scenario: Consumer resources cleaned up after Router stops
- **WHEN** the Watermill Router stops due to context cancellation
- **THEN** `Shutdown(context.Background())` is called, and all closers (database, telemetry, publisher) execute with a live context

#### Scenario: Router explicitly closed before resource teardown
- **WHEN** shutdown begins in the consumer
- **THEN** `Router.Close()` is called explicitly and blocks until all in-flight message handlers complete or `CloseTimeout` is reached, before infrastructure closers run

### Requirement: Signal Cause Logging
The application SHALL log the specific OS signal that triggered shutdown using Go 1.26 `context.Cause()`.

#### Scenario: SIGTERM logged with cause
- **WHEN** the process receives SIGTERM
- **THEN** the shutdown log entry includes `cause: "signal: terminated"` (or equivalent signal string)

#### Scenario: SIGINT logged with cause
- **WHEN** the process receives SIGINT
- **THEN** the shutdown log entry includes `cause: "signal: interrupt"`

### Requirement: Shutdown Timeout Budget Alignment
The application's internal `SHUTDOWN_TIMEOUT` MUST be less than `terminationGracePeriodSeconds` minus the `preStop` delay, leaving at least a 10-second safety buffer.

#### Scenario: API server timeout budget
- **WHEN** the API server deployment has `terminationGracePeriodSeconds: 60` and `preStop: sleep 5`
- **THEN** `SHUTDOWN_TIMEOUT` SHALL be at most 45s (60 - 5 - 10 buffer)

#### Scenario: Consumer timeout budget
- **WHEN** the consumer deployment has `terminationGracePeriodSeconds: 90` and `preStop: sleep 5`
- **THEN** `SHUTDOWN_TIMEOUT` SHALL be at most 60s (90 - 5 - 25 buffer)
