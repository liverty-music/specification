# Frontend Hosting

## Purpose

This capability provides infrastructure and deployment workflows for hosting the Aurelia 2 frontend single-page application (SPA) on Kubernetes. It encompasses container image builds, static asset serving, client-side routing support, HTTPS ingress, and GitOps-based deployment automation.

The frontend hosting capability ensures the compiled frontend application is:
- Packaged as a lightweight container image with Caddy web server
- Deployed to GKE using the same GitOps patterns as the backend
- Accessible over HTTPS with automatic TLS certificate management
- Optimized for SPA routing and static asset caching

## Requirements

### Requirement: Container image build pipeline
The system SHALL provide an automated container image build pipeline that produces a production-ready Docker image containing the compiled frontend application and Caddy web server.

#### Scenario: Successful multi-stage build on main branch push
- **WHEN** code is pushed to the main branch of the frontend repository
- **THEN** GitHub Actions SHALL trigger a multi-stage Docker build using Node 22 for compilation and Caddy 2 Alpine for runtime
- **THEN** the build SHALL produce a final image containing only static assets and Caddy runtime (no Node or build tools)
- **THEN** the image SHALL be tagged with the Git commit SHA
- **THEN** the image SHALL be pushed to Google Artifact Registry

#### Scenario: Build includes Vite compilation
- **WHEN** the Docker build executes the builder stage
- **THEN** the system SHALL run `npm ci` to install dependencies
- **THEN** the system SHALL run `npm run build` to compile the Aurelia 2 application with Vite
- **THEN** the system SHALL output static assets to the `/dist` directory

### Requirement: Kubernetes deployment configuration
The system SHALL deploy the frontend application to a dedicated Kubernetes namespace using Kustomize-based manifests managed by ArgoCD.

#### Scenario: Deployment manifest defines pod specification
- **WHEN** ArgoCD syncs the frontend namespace
- **THEN** a Deployment resource SHALL be created in the `frontend` namespace
- **THEN** the Deployment SHALL specify 1 replica initially
- **THEN** the Deployment SHALL reference the frontend container image from Google Artifact Registry
- **THEN** the Deployment SHALL configure resource requests of 50m CPU and 64Mi memory
- **THEN** the Deployment SHALL configure resource limits of 200m CPU and 128Mi memory
- **THEN** the Deployment SHALL use spot VMs via nodeSelector or tolerations

#### Scenario: Service exposes deployment
- **WHEN** ArgoCD syncs the frontend namespace
- **THEN** a ClusterIP Service SHALL be created targeting the Deployment on port 80
- **THEN** the Service SHALL route traffic to the Caddy container port

### Requirement: Static asset serving with caching
The system SHALL serve static HTML, JavaScript, and CSS assets efficiently using Caddy web server with appropriate HTTP caching headers.

#### Scenario: Root path serves index.html
- **WHEN** a user requests `https://dev.liverty-music.app/`
- **THEN** Caddy SHALL respond with `index.html` from the `/srv` directory
- **THEN** the response SHALL include cache headers that prevent long-term caching (e.g., `Cache-Control: no-cache` or short `max-age`) to ensure users always receive the latest HTML

#### Scenario: Asset files are served with long-term caching
- **WHEN** a user requests a versioned asset file (e.g., `/assets/main.abc123.js`)
- **THEN** Caddy SHALL serve the file from `/srv/assets/`
- **THEN** the response SHALL include cache headers allowing long-term browser caching

### Requirement: SPA client-side routing support
The system SHALL support client-side routing by serving `index.html` for all routes that do not match static files, enabling Aurelia 2's router to handle navigation.

#### Scenario: Non-existent route returns index.html
- **WHEN** a user directly accesses a client-side route (e.g., `https://dev.liverty-music.app/concerts`)
- **THEN** Caddy SHALL check if a static file exists at that path
- **THEN** Caddy SHALL respond with `index.html` (not 404) if no static file is found
- **THEN** the Aurelia 2 router SHALL handle the route on the client side

#### Scenario: Static assets are not affected by fallback
- **WHEN** a user requests a static asset (e.g., `/favicon.ico` or `/assets/style.css`)
- **THEN** Caddy SHALL serve the actual file directly
- **THEN** Caddy SHALL NOT fallback to `index.html`

### Requirement: HTTPS ingress via Gateway API
The system SHALL expose the frontend application over HTTPS using GKE Gateway API with automatic TLS certificate management.

#### Scenario: HTTPRoute binds to Gateway
- **WHEN** ArgoCD syncs the frontend namespace
- **THEN** an HTTPRoute resource SHALL be created in the `frontend` namespace
- **THEN** the HTTPRoute SHALL reference `external-gateway` in the `gateway` namespace
- **THEN** the HTTPRoute SHALL configure hostname `dev.liverty-music.app`
- **THEN** the HTTPRoute SHALL route all traffic to the frontend Service on port 80

#### Scenario: TLS certificate is provisioned
- **WHEN** the HTTPRoute is created with hostname `dev.liverty-music.app`
- **THEN** the existing `api-gateway-cert-map` SHALL include a certificate for this domain
- **THEN** the Gateway SHALL serve the frontend over HTTPS (port 443)
- **THEN** HTTP requests SHALL be redirected to HTTPS

### Requirement: GitOps deployment automation
The system SHALL manage frontend deployments using ArgoCD following the same GitOps pattern as the backend, with manifests stored in the cloud-provisioning repository.

#### Scenario: ArgoCD Application watches cloud-provisioning repository
- **WHEN** an ArgoCD Application resource is created for the frontend
- **THEN** ArgoCD SHALL monitor `cloud-provisioning/k8s/namespaces/frontend/overlays/dev` on the main branch
- **THEN** ArgoCD SHALL automatically sync changes to the cluster
- **THEN** ArgoCD SHALL enable auto-prune and self-heal policies

#### Scenario: Kustomize overlays customize per environment
- **WHEN** ArgoCD applies the frontend manifests
- **THEN** Kustomize SHALL use `base/` manifests as the foundation
- **THEN** Kustomize SHALL apply `overlays/dev/` patches for dev-specific configuration
- **THEN** the dev overlay SHALL override the HTTPRoute hostname to `dev.liverty-music.app`

### Requirement: Caddyfile configuration
The system SHALL configure Caddy web server using a declarative Caddyfile that defines serving behavior and SPA routing logic.

#### Scenario: Caddyfile defines root and file server
- **WHEN** the Caddy container starts
- **THEN** the Caddyfile SHALL specify `root * /srv` to set the document root
- **THEN** the Caddyfile SHALL enable `file_server` to serve static files
- **THEN** the Caddyfile SHALL listen on port 80

#### Scenario: Caddyfile configures SPA fallback
- **WHEN** Caddy receives a request
- **THEN** the Caddyfile SHALL use `try_files {path} /index.html` directive
- **THEN** Caddy SHALL attempt to serve the requested path first
- **THEN** Caddy SHALL fallback to `index.html` if the path does not exist

### Requirement: DNS and TLS infrastructure provisioning
The system SHALL provision DNS records and TLS certificates for the frontend domain using Pulumi infrastructure-as-code, following the existing shared Gateway pattern.

#### Scenario: DNS A record points to shared static IP
- **WHEN** Pulumi provisions the network infrastructure for dev environment
- **THEN** a DNS A record SHALL be created for `dev.liverty-music.app` in the Cloud DNS public zone
- **THEN** the A record SHALL point to the existing `api-gateway-static-ip` address (shared with backend)
- **THEN** the A record SHALL have a TTL of 300 seconds
- **THEN** the A record resource name SHALL be `web-app-a-record`

#### Scenario: TLS certificate covers frontend domain
- **WHEN** Pulumi provisions certificate infrastructure
- **THEN** a DNS Authorization SHALL be created for `dev.liverty-music.app` domain
- **THEN** the existing `api-gateway-cert` Certificate resource SHALL include both `api.dev.liverty-music.app` and `dev.liverty-music.app` in its managed domains list
- **THEN** the Certificate SHALL reference DNS authorizations for both domains
- **THEN** a CNAME record SHALL be created in Cloud DNS for ACME challenge validation of the frontend domain

#### Scenario: Certificate map includes frontend domain
- **WHEN** Pulumi provisions the certificate map
- **THEN** a CertificateMapEntry SHALL be created with name `web-app-cert-map-entry`
- **THEN** the entry SHALL map hostname `dev.liverty-music.app` to the `api-gateway-cert` certificate
- **THEN** the entry SHALL be added to the existing `api-gateway-cert-map`
- **THEN** the Gateway API SHALL use this cert map for TLS termination

#### Scenario: Infrastructure follows shared Gateway pattern
- **WHEN** deploying to dev environment
- **THEN** frontend and backend SHALL share the same static IP address
- **THEN** frontend and backend SHALL share the same GKE Gateway resource
- **THEN** frontend and backend SHALL share the same certificate map
- **THEN** routing differentiation SHALL be handled by HTTPRoute hostname matching
