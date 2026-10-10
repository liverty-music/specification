# components/infrastructure/backend/process/startup-dependencies Specification

## Purpose
How every backend process — an API server, an event consumer or a job — treats the message broker, the sign-in service and the database while it starts, so that a dependency that is briefly unreachable never stops the process.

## Requirements

### Requirement: A briefly unreachable dependency does not end the process

A backend process SHALL NOT exit because the message broker, the sign-in service or the database is unreachable while it starts. It SHALL keep trying to reach each dependency it needs before it can work for at least 5 minutes. Only after that SHALL it give up and exit with a failure.

#### Scenario: Broker back within the wait

- **WHEN** an event consumer starts while the message broker is unreachable, and the broker becomes reachable 2 minutes later
- **THEN** the consumer starts consuming without having exited or restarted

#### Scenario: Database unreachable beyond the wait

- **WHEN** a backend process starts and the database stays unreachable for 6 minutes
- **THEN** the process keeps trying for at least 5 minutes and then exits with a failure

### Requirement: An API server serves without the message broker

An API server SHALL become ready while the message broker is unreachable, and SHALL serve calls whose effect does not depend on the broker. A call that also publishes an event SHALL still complete its own effect and return within 10 seconds of attempting the publish.

#### Scenario: Start while the broker is down

- **WHEN** an API server starts while the message broker is unreachable and the database is reachable
- **THEN** the server becomes ready, and a call that only reads data succeeds

#### Scenario: Follow while the broker is down

- **WHEN** a fan follows an artist while the message broker is unreachable
- **THEN** the follow is stored and the call returns within 10 seconds

### Requirement: The sign-in service is reached on first use

A backend process SHALL NOT contact the sign-in service while it starts. A call that needs the sign-in service while that service is unreachable SHALL fail as the operation it uses specifies. The first such call after the service recovers SHALL succeed, without the process restarting.

#### Scenario: Start while the sign-in service is down

- **WHEN** an API server starts while the sign-in service is unreachable
- **THEN** the server becomes ready and serves calls that do not need the sign-in service

#### Scenario: Recovery without restart

- **WHEN** a call that removes a sign-in identity fails because the sign-in service is unreachable, and the service then recovers
- **THEN** the next such call succeeds, without the process having restarted
