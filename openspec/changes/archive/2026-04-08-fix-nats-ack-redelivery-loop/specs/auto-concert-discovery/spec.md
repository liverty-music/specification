## ADDED Requirements

### Requirement: Consumer JetStream Delivery Policy

The NATS JetStream consumer SHALL use `DeliverNew` delivery policy so that a newly created durable consumer only receives messages published after its creation time, preventing historical message redelivery when consumer state is lost due to infrastructure events (e.g., cluster migration, PVC recreation).

#### Scenario: First consumer creation after state loss

- **WHEN** the durable JetStream consumer is created for the first time (no prior consumer state exists)
- **THEN** the consumer SHALL only receive messages published from that point forward
- **AND** messages published before consumer creation SHALL NOT be redelivered

#### Scenario: Consumer reconnects to existing durable

- **WHEN** a consumer pod restarts and reconnects to an existing durable consumer
- **THEN** the consumer SHALL resume from the last acknowledged message sequence
- **AND** the delivery policy SHALL have no effect on reconnection behavior

### Requirement: Consumer JetStream Acknowledgement Policy

The NATS JetStream consumer SHALL use synchronous acknowledgement (`AckSync`) to guarantee that a message's Ack is confirmed by the NATS server before the handler is considered complete, preventing message redelivery due to lost Acks during pod shutdown.

#### Scenario: Successful message processing

- **WHEN** a message handler completes successfully
- **THEN** the consumer SHALL wait for NATS server confirmation of the Ack before marking the handler as done
- **AND** the NATS JetStream consumer lag SHALL reflect the acknowledged message as processed

#### Scenario: Simultaneous pod scale-down

- **WHEN** KEDA scales down multiple consumer pods simultaneously
- **THEN** all in-flight Acks SHALL be confirmed by the NATS server before pod shutdown completes
- **AND** KEDA SHALL observe consumer lag = 0 after scale-down
- **AND** KEDA SHALL NOT re-activate the consumer deployment within the cooldown period
