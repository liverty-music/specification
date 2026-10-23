## Purpose

How a unit of work keeps one trace while it passes through backend processes: an API request, a scheduled job and the event consumers that the work triggers through the message broker all record their part under the same trace, so one discovery, delivery or order can be followed from start to end in the traces and the logs.

## ADDED Requirements

### Requirement: An event carries the trace of the work that published it

When a backend process publishes an event while it handles a unit of work, the event SHALL carry that work's trace context. The event consumer that handles the event SHALL record its handling as part of the same trace, as a child of the publishing step. This SHALL hold for every event consumer and through every hop: an event that a consumer publishes while handling an event carries the same trace again. The event's payload and its other attributes SHALL stay as they are.

#### Scenario: Consumer continues the publisher's trace

- **WHEN** a concert search publishes the discovered concerts and the event consumer that stores them handles that event
- **THEN** the consumer's handling is recorded in the same trace as the search, and its log lines carry the search's trace id

#### Scenario: Two hops

- **WHEN** an event consumer publishes a second event while it handles the first, and another consumer handles the second
- **THEN** all three steps are recorded in one trace

#### Scenario: Event without trace context

- **WHEN** a consumer receives an event that carries no trace context, such as one published before this rule applied
- **THEN** the consumer handles the event as usual and records it in a new trace

#### Scenario: Redelivered event

- **WHEN** the message broker delivers an event again after a failed handling
- **THEN** the new attempt is recorded in the trace the event carries

### Requirement: A scheduled job records its work in traces

A scheduled job SHALL record each run as a trace. A job that processes artists one at a time and calls an external search for each SHALL record each artist as its own trace, linked to the trace of the run. Every log line the job writes while it handles an artist SHALL carry that artist's trace id, and every event it publishes for the artist SHALL carry that trace.

#### Scenario: One trace per artist

- **WHEN** the concert discovery job searches 3 followed artists in one run
- **THEN** 3 artist traces are recorded, each linked to the run's trace, and the log lines of each search carry that artist's trace id

#### Scenario: Job that publishes events

- **WHEN** the ticket sale reminder job publishes a reminder event
- **THEN** the event carries the trace of the job run, and the consumer that delivers the reminder records its handling in that trace
