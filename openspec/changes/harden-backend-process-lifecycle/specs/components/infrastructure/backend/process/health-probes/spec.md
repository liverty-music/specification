## Purpose

What the liveness and readiness checks of backend API servers and event consumers report. The platform should restart only a process that cannot recover by itself, and should route traffic only to a process that can serve it, without the checks adding load to the database.

## ADDED Requirements

### Requirement: API liveness reflects only the process

An API server's liveness check SHALL report alive whenever the process can answer it, whether or not the database, the message broker or the sign-in service is reachable.

#### Scenario: Database unreachable

- **WHEN** the database becomes unreachable while an API server is running
- **THEN** its liveness check keeps reporting alive, and the process is not restarted

### Requirement: API readiness reflects the database

An API server's readiness check SHALL report not ready while the database cannot be reached, and while the server is shutting down. Otherwise it SHALL report ready.

#### Scenario: Database unreachable

- **WHEN** the database cannot be reached
- **THEN** the readiness check reports not ready, and reports ready again once the database is reachable

#### Scenario: Shutting down

- **WHEN** the server has begun shutting down
- **THEN** the readiness check reports not ready

### Requirement: Health checks add no database load

However many readiness checks an API server receives at once, it SHALL run at most one database check at a time, using at most one database connection for health checks. It SHALL answer from a result at most 5 seconds old. A slow or unreachable database SHALL NOT make health checks open more database connections.

#### Scenario: Concurrent checks against a slow database

- **WHEN** 10 readiness checks arrive within one second while each database check takes 8 seconds
- **THEN** one database check runs, all 10 checks share its result, and the server holds no more database connections than before the checks

### Requirement: Event consumer liveness reflects consumption, not broker reachability

An event consumer's liveness check SHALL report not alive when the consumer is connected to the message broker but has not been consuming every subscription it expects for 2 minutes. While the consumer is disconnected from the broker and reconnecting, its liveness check SHALL keep reporting alive.

#### Scenario: Broker restarts

- **WHEN** the message broker is unreachable for 3 minutes while an event consumer is running
- **THEN** the consumer is not restarted, and it resumes consuming once the broker is reachable

#### Scenario: Connected but not consuming

- **WHEN** an event consumer is connected to the broker, but one of its expected subscriptions has stayed unbound for 2 minutes
- **THEN** its liveness check reports not alive, and the process is restarted
