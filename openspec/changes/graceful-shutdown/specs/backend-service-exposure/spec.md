## MODIFIED Requirements

### Requirement: Health Check Integration
The backend Service SHALL be health-checked by external load balancer using gRPC health protocol. Additionally, the health check handler SHALL reflect application shutdown state by returning `NOT_SERVING` immediately upon SIGTERM receipt.

#### Scenario: Health probe reaches pod
- **WHEN** HealthCheckPolicy targets server Service with gRPC type
- **THEN** load balancer periodically calls grpc.health.v1.Health.Check on port 8080

#### Scenario: Pod readiness propagated
- **WHEN** backend Pod implements gRPC health checks
- **THEN** healthy Pods are marked as backends; unhealthy Pods are drained

#### Scenario: Shutdown state reflected in health response
- **WHEN** Pod receives SIGTERM and health check is called during shutdown
- **THEN** health check returns `NOT_SERVING`, causing load balancer to stop routing new traffic to the Pod

## ADDED Requirements

### Requirement: Pod Graceful Termination Configuration
All backend Deployments and CronJobs SHALL configure explicit `terminationGracePeriodSeconds` and `preStop` lifecycle hooks to ensure zero-downtime rolling deployments.

#### Scenario: Server deployment preStop delay
- **WHEN** a server Pod is terminated during a rolling update
- **THEN** the `preStop` hook delays SIGTERM by 5 seconds, allowing the load balancer to remove the Pod from its backend pool

#### Scenario: Server termination grace period
- **WHEN** a server Pod shutdown exceeds the application's `SHUTDOWN_TIMEOUT`
- **THEN** K8s waits up to `terminationGracePeriodSeconds` (60s) before sending SIGKILL

#### Scenario: Consumer termination grace period
- **WHEN** a consumer Pod is terminated
- **THEN** K8s waits up to `terminationGracePeriodSeconds` (90s) to allow in-flight message handlers to complete

### Requirement: Consumer Health Probes
The consumer Deployment SHALL expose health probes so that K8s can detect hangs and NATS disconnections.

#### Scenario: Consumer readiness probe
- **WHEN** the consumer's Watermill Router is running and connected to NATS
- **THEN** the readiness probe returns HTTP 200 on port 8081 `/readyz`

#### Scenario: Consumer liveness probe
- **WHEN** the consumer process is alive
- **THEN** the liveness probe returns HTTP 200 on port 8081 `/healthz`

#### Scenario: Consumer shutdown reflected in readiness
- **WHEN** the consumer receives SIGTERM
- **THEN** the readiness probe returns HTTP 503, signaling K8s to stop routing traffic
