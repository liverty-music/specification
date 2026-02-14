## ADDED Requirements

### Requirement: Backend Service Accessibility from External Gateway
The system SHALL make the `server` Service (backend namespace) accessible to HTTPRoute resources in the `gateway` namespace.

#### Scenario: Service discovered by Gateway
- **WHEN** HTTPRoute references Service server with namespace: backend
- **THEN** load balancer resolves the Service and routes traffic to its endpoints

#### Scenario: Service IP stable
- **WHEN** server Service is in ClusterIP mode
- **THEN** load balancer can reach backend pods via stable cluster IP

### Requirement: Service Protocol Configuration for HTTP/2
The system SHALL configure the backend Service with `appProtocol: kubernetes.io/h2c` to indicate HTTP/2 clear text support.

#### Scenario: h2c protocol detected
- **WHEN** Service port has appProtocol: kubernetes.io/h2c
- **THEN** load balancer communicates with backend using HTTP/2 (without TLS)

#### Scenario: Health checks use HTTP/2
- **WHEN** HealthCheckPolicy is configured for gRPC protocol
- **THEN** load balancer health probes use HTTP/2 h2c to port 8080

### Requirement: Cross-Namespace Routing Enabled
The system SHALL allow Gateway listeners to accept HTTPRoute resources from any namespace via `allowedRoutes.namespaces.from: All`.

#### Scenario: HTTPRoute from gateway namespace accepted
- **WHEN** HTTPRoute in gateway namespace has parentRef to Gateway in same namespace
- **THEN** HTTPRoute rules are attached to Gateway listeners

### Requirement: Backend Pods Targeted via Service
The system SHALL ensure backend Pods (matched by Service selector) receive routed traffic.

#### Scenario: Traffic reaches pod
- **WHEN** load balancer forwards request to Service cluster IP port 8080
- **THEN** traffic reaches backend Pod running Connect-RPC server (port 8080)

#### Scenario: Multiple backend replicas load-balanced
- **WHEN** Deployment has replicas > 1
- **THEN** load balancer distributes requests across all ready Pods

### Requirement: No Direct Pod Exposure
The system SHALL NOT expose Pods directly; all traffic flows through Service abstraction.

#### Scenario: Service load balancing enforced
- **WHEN** backend Pod terminates and new Pod starts
- **THEN** Service seamlessly routes to new Pod, client requests unaffected

### Requirement: Namespace Isolation Maintained
The system SHALL NOT allow Services outside backend namespace to be exposed via this Gateway without explicit HTTPRoute configuration.

#### Scenario: Accidental service not exposed
- **WHEN** unrelated Service exists in different namespace
- **THEN** Gateway only routes to Services explicitly listed in HTTPRoute backendRefs
