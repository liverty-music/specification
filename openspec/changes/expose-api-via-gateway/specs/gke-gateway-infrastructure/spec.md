## ADDED Requirements

### Requirement: Gateway API Resource Creation
The system SHALL provide a GKE Gateway API resource that listens on HTTPS (443) and HTTP (80) ports, deployed in the `gateway` namespace.

#### Scenario: HTTPS listener active
- **WHEN** a request arrives at the static IP on port 443
- **THEN** the Gateway terminates TLS and routes to HTTPRoute rules

#### Scenario: HTTP listener redirects
- **WHEN** a request arrives at port 80
- **THEN** the Gateway returns HTTP 301 redirect to HTTPS

### Requirement: HTTPRoute API Routing
The system SHALL provide HTTPRoute resources that route traffic from the Gateway to the backend Service based on hostname and path matching.

#### Scenario: API requests routed correctly
- **WHEN** a request matches hostname `api.liverty-music.app` and path `/`
- **THEN** the request is forwarded to `backend/server:8080` Service

#### Scenario: Path prefix matching
- **WHEN** a request to `api.liverty-music.app/liverty_music.rpc.*/` arrives
- **THEN** the request is matched and routed to backend

### Requirement: GatewayClass Selection
The system SHALL use `gke-l7-global-external-managed` as the GatewayClass for global external load balancing.

#### Scenario: Global ALB provisioned
- **WHEN** Gateway resource is applied with gatewayClassName: gke-l7-global-external-managed
- **THEN** GKE provisions a Global External Application Load Balancer

### Requirement: Cross-Namespace Routing
The system SHALL allow HTTPRoute (gateway namespace) to reference Services in other namespaces (backend namespace).

#### Scenario: Service discovered across namespaces
- **WHEN** HTTPRoute specifies backendRefs.namespace: backend
- **THEN** the load balancer can reach the Service in the backend namespace

### Requirement: Certificate Management Annotation
The system SHALL bind TLS certificates to the Gateway via annotation `networking.gke.io/certmap`.

#### Scenario: Certificate mapped to listener
- **WHEN** Gateway.metadata.annotations["networking.gke.io/certmap"] = "api-cert-map"
- **THEN** the HTTPS listener uses certificates from Certificate Manager map

### Requirement: Policy Attachment for Gateway Configuration
The system SHALL support GCPGatewayPolicy for configuring Gateway-level settings such as SSL policies and global access.

#### Scenario: Gateway policy applied
- **WHEN** GCPGatewayPolicy targets the external-gateway
- **THEN** SSL policy and access settings are applied to the Gateway
