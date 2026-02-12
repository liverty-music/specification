## MODIFIED Requirements

### Requirement: Backend Service Discoverability
The backend Service SHALL be discoverable by external load balancers (Gateway) via explicit cross-namespace references.

#### Scenario: Service referenced by Gateway
- **WHEN** HTTPRoute in gateway namespace specifies backendRef to server Service in backend namespace
- **THEN** Service is resolved and traffic routed to its endpoints

#### Scenario: Service remains internal
- **WHEN** Service is ClusterIP type (not LoadBalancer or NodePort)
- **THEN** Service is only accessible via Gateway within cluster, not directly from internet

### Requirement: Service Backend Protocol Support
The backend Service SHALL advertise HTTP/2 clear text support via appProtocol field.

#### Scenario: h2c advertised
- **WHEN** Service port has appProtocol: kubernetes.io/h2c
- **THEN** load balancer knows it can communicate with backend using HTTP/2 without TLS encryption

### Requirement: Health Check Integration
The backend Service SHALL be health-checked by external load balancer using gRPC health protocol.

#### Scenario: Health probe reaches pod
- **WHEN** HealthCheckPolicy targets server Service with gRPC type
- **THEN** load balancer periodically calls grpc.health.v1.Health.Check on port 8080

#### Scenario: Pod readiness propagated
- **WHEN** backend Pod implements gRPC health checks
- **THEN** healthy Pods are marked as backends; unhealthy Pods are drained
