# components/infrastructure/backend/process/durable-workflows Specification

## Purpose
How a backend workflow, a business process written as ordered steps, survives a stopped process, which process runs it and when that process is ready, how its failures are retried and reported, how the events it announces keep one id, and how long its records are kept.

## Requirements

### Requirement: A started workflow resumes after a stop

A workflow that was started SHALL run to its end even when the process running it stops. When that process starts again, the workflow SHALL continue with the step after its last completed one; a completed step SHALL NOT run again, and its recorded result SHALL be used instead. Starting a workflow again with the id of one that exists SHALL NOT start a second run: the caller SHALL get the existing run and its result.

#### Scenario: Worker stops between two steps
- **WHEN** the workflow worker stops after the first of two steps of a workflow completed and starts again
- **THEN** the workflow runs only its second step and ends

#### Scenario: Same workflow started twice
- **WHEN** two API servers start a workflow with the same id at the same time
- **THEN** it runs once and both get its result

### Requirement: Only the workflow worker runs workflows

The workflow worker SHALL be the only backend process that runs workflows, their queues and their schedules, and at most one workflow worker SHALL run at a time, also while it is redeployed. API servers, event consumers and jobs SHALL only start workflows, send them signals and wait for their results.

#### Scenario: Worker redeployed
- **WHEN** the workflow worker is redeployed while a workflow is waiting between two steps
- **THEN** the old worker stops before the new one starts, and the new one continues the workflow

#### Scenario: API server restarts
- **WHEN** an API server that started a workflow restarts while the workflow runs
- **THEN** the workflow keeps running in the workflow worker

### Requirement: The workflow worker is ready only once it runs workflows

The workflow worker SHALL report ready only after it has connected to the database and started running its queues and schedules. Its liveness check SHALL report alive whenever the process can answer it, whether or not the database is reachable.

#### Scenario: Database unreachable at start
- **WHEN** the workflow worker starts while the database is unreachable for 3 minutes
- **THEN** it reports not ready, keeps trying, stays alive, and reports ready once it runs its queues and schedules

### Requirement: Transient failures are retried; a workflow that cannot finish is reported

A step that fails with Unavailable or DeadlineExceeded SHALL be tried again, first after 1 second and then at doubling intervals of at most 1 hour, until it succeeds or the workflow's deadline passes. A business outcome, such as a card that can no longer be charged, SHALL be a result of the workflow, not a failure. A workflow SHALL be reported for an admin within 5 minutes, and SHALL stay reported until an admin resumes or deletes it, when it ends with any other error, when its process stopped during it more than 100 times, or when it passes its deadline.

#### Scenario: Payment provider unavailable for 10 minutes
- **WHEN** a step fails with Unavailable for 10 minutes and then succeeds
- **THEN** the workflow continues after it and nothing is reported

#### Scenario: Unexpected error
- **WHEN** a step fails with Internal
- **THEN** the workflow ends with that error and is reported for an admin within 5 minutes, with its id and name

#### Scenario: Deadline passed
- **WHEN** a workflow with a 24-hour deadline still retries a step after 24 hours
- **THEN** it stops and is reported for an admin

### Requirement: An announcement from a workflow has one id

An event that a workflow step publishes SHALL carry an id derived from the workflow's id and the step, so the event has the same id every time the step runs. Consumers SHALL treat events with the same id as one.

#### Scenario: Step runs again after a stop
- **WHEN** the worker stops after publishing an event and before recording the step, and the step runs again
- **THEN** the event is published again with the same id, and product analytics records it once

### Requirement: Workflow records are kept for 30 days

Once a day, the records of every workflow that ended successfully and was started more than 30 days before SHALL be deleted. A workflow that has not ended, or that is reported for an admin, SHALL NOT be deleted by this, whatever its age; it is deleted only when an admin resolves it.

#### Scenario: Old finished workflow
- **WHEN** a workflow started 31 days ago and ended successfully
- **THEN** its record is deleted by the next daily run

#### Scenario: Old failed workflow
- **WHEN** a workflow started 31 days ago ended with an unexpected error and no admin has resolved it
- **THEN** its record is kept and it is still reported for an admin

#### Scenario: Workflow still waiting
- **WHEN** a workflow started 40 days ago is still waiting
- **THEN** its record is kept
