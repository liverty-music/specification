## ADDED Requirements

### Requirement: A scheduled workflow records only the work it starts

A workflow that runs on a schedule to look for due work SHALL record no trace for a run that finds nothing. Each workflow such a run starts SHALL be recorded as its own trace, not as part of the scheduled run, and the work that the started workflow triggers SHALL continue that trace.

#### Scenario: Scheduled run that finds no due sale

- **WHEN** the scheduled check for Lottery sales due a draw runs and finds none
- **THEN** no trace is recorded for the run, and its log lines carry a trace id

#### Scenario: Scheduled run that finds a due sale

- **WHEN** the scheduled check finds one Lottery sale due a draw and starts its draw
- **THEN** the draw is recorded as a new trace, and the issuance and card authorization releases started for its entries are recorded in that trace
