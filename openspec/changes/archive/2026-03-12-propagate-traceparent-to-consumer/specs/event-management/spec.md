## ADDED Requirements

### Requirement: Trace context propagation across message broker

The system SHALL propagate W3C Trace Context (traceparent) from the publisher process to the consumer process via message metadata. Consumer-side structured logs SHALL include `trace_id` and `span_id` fields extracted from the propagated trace context.

#### Scenario: Consumer log includes trace fields from publisher trace

- **WHEN** a publisher emits an event while processing a traced request
- **THEN** the consumer handler's structured logs MUST contain `trace_id` and `span_id` fields matching the publisher's trace

#### Scenario: Consumer handler operates within propagated span

- **WHEN** the consumer receives a message with trace context in its metadata
- **THEN** all downstream operations (database queries, nested event publishing) MUST be children of the propagated trace
