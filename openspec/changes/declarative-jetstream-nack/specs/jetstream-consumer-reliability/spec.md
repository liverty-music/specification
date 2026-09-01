## MODIFIED Requirements

### Requirement: Stream and durable configuration is managed declaratively by a single owner

JetStream stream and consumer (durable) configuration SHALL be managed
**declaratively by a single in-cluster controller that exclusively owns those
resources**. The declared configuration SHALL be the source of truth, and the
controller SHALL correct drift (recreating a durable whose server-stored
configuration — name, deliver group, or delivery policy — differs from the
declared one) so a configuration or naming change cannot wedge on a stale
pre-existing durable. Application workloads SHALL NOT create streams, and SHALL
NOT run a global reconcile that deletes durables; a consumer workload SHALL
**bind** to the pre-existing declared durable rather than create it. This removes
the failure mode where a second consumer application, reconciling only its own
subset of durables, deletes the durables owned by another application.

#### Scenario: A pre-existing durable has drifted configuration

- **WHEN** a durable exists on the server with a configuration that differs from
  the declared configuration
- **THEN** the controller SHALL recreate that durable to match the declared
  configuration, and consumers SHALL bind to the corrected durable

#### Scenario: An already-correct durable is adopted as a no-op

- **WHEN** a durable already matches the declared configuration
- **THEN** the controller SHALL leave it untouched (no delete/recreate, no cursor
  reset, no deliver-group change) and consumer workloads SHALL bind to it

#### Scenario: One consumer application never deletes another's durables

- **WHEN** multiple consumer workloads exist, each consuming a different subset of
  durables
- **THEN** no workload SHALL delete a durable it does not consume; durable
  lifecycle SHALL be governed only by the declared configuration and its owning
  controller

## ADDED Requirements

### Requirement: A consumer may scale to zero without losing its durable

A JetStream consumer workload MAY scale to **zero replicas** while its durable
continues to exist independently of the workload. The autoscaler SHALL still
observe the durable's backlog while the workload is at zero and SHALL wake the
workload when messages arrive; messages published while the workload is at zero
SHALL be retained and delivered once it wakes.

#### Scenario: A message published while idle wakes the workload and is processed

- **WHEN** a consumer workload is at zero replicas and a message is published to
  its stream
- **THEN** the durable SHALL retain the message, the autoscaler SHALL observe the
  pending backlog and scale the workload up, and the workload SHALL process the
  message

#### Scenario: No replicas run while there is no work

- **WHEN** a scale-to-zero consumer workload has no pending messages for its
  cooldown window
- **THEN** the workload SHALL run zero replicas, while its durable remains present
  for the autoscaler to observe
