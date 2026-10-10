# components/infrastructure/backend/process/structured-logging Specification

## Purpose
The format of every log line a deployed backend process emits. The log collector should record each line at its true severity, so that error alerts see every failure, including failures while the process starts.

## Requirements

### Requirement: Every log line carries its severity

Every log line a deployed backend process writes SHALL be one single-line JSON object, which the log collector records at the line's own severity. This SHALL hold from the first line the process writes until it exits, including lines written before the process is ready and the line that reports why it exits.

#### Scenario: Startup message

- **WHEN** a backend process starts
- **THEN** its start-up message is recorded at INFO

#### Scenario: Process gives up at startup

- **WHEN** a backend process exits because a dependency stayed unreachable beyond its startup wait
- **THEN** the reason is recorded at ERROR as one entry that names the unreachable dependency

### Requirement: Normal stops and retries are not errors

A backend process SHALL NOT log at ERROR when it stops normally, when its health endpoint stops as part of shutdown, or when it cleans up after a start that failed. A retry while waiting for a dependency SHALL be logged at WARNING. When a start fails, the failure itself SHALL be the only ERROR entry for that start.

#### Scenario: Normal shutdown

- **WHEN** an event consumer is stopped during a rollout
- **THEN** no entry is recorded at ERROR

#### Scenario: Waiting for the broker

- **WHEN** an event consumer retries reaching the message broker during startup
- **THEN** each retry is recorded at WARNING

#### Scenario: Failed start

- **WHEN** a backend process gives up at startup
- **THEN** exactly one entry is recorded at ERROR for that start
