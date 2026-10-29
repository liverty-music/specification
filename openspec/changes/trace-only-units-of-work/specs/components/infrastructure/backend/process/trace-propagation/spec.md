## ADDED Requirements

### Requirement: Work outside a unit of work records no trace

A unit of work is an API request, the handling of an event, a job run or a workflow run. A backend process SHALL record a database query or an outgoing call in a trace only when it makes the query or call while it handles a unit of work. A query or call made outside any unit of work, such as a periodic check that runs in the background of a process or a refresh of the database connection's credentials, SHALL record no trace. Every log line written outside a unit of work SHALL still carry a trace id.

#### Scenario: Background check that finds nothing

- **WHEN** a periodic check in the background of the fan API queries the database every minute and finds nothing to do
- **THEN** no trace is recorded for the check, and its log lines carry a trace id

#### Scenario: Database credential refresh

- **WHEN** a backend process refreshes the credentials of its database connection
- **THEN** no trace is recorded for the refresh

#### Scenario: Same query inside a request

- **WHEN** a fan's API request runs a database query
- **THEN** the query is recorded in the request's trace, as a child of the request
