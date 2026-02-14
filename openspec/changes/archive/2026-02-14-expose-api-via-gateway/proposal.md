## Why

The Connect-RPC backend server (port 8080) is currently only accessible from within the GKE cluster. To enable the Aurelia 2 PWA frontend to communicate with the backend, we need to expose the API through a public HTTPS endpoint. Using GKE Gateway API provides a modern, cloud-native approach with integrated TLS termination, health checks, and scalability.

## What Changes

- Create public Cloud DNS zone for `liverty-music.app` domain in GCP via Pulumi (configured via ESC)
- Add GKE Gateway API infrastructure (Gateway, HTTPRoute, Policies) in a dedicated `gateway` namespace for LB management separation
- Implement CORS support in the Connect-RPC server using `connectrpc.com/cors` package
- Configure Google-managed SSL certificates via Certificate Manager with automatic DNS authentication
- Set up cross-namespace routing from Gateway (gateway ns) to backend Service (backend ns)
- Create health check policies for gRPC health protocol monitoring
- Deploy via Kustomize (base/overlays) pattern matching existing infrastructure code
- Integrate with ArgoCD for GitOps-based deployment

## Capabilities

### New Capabilities

- `cloud-dns-infrastructure`: Hybrid DNS architecture using Cloudflare DNS for production (`liverty-music.app`, Proxy OFF) and Cloud DNS for dev environment (`dev.liverty-music.app`) via subdomain delegation, managed through Pulumi with ESC configuration
- `gke-gateway-infrastructure`: GKE Gateway API resources (Gateway, HTTPRoute, Policies) for exposing services on public IPs with TLS termination
- `connect-rpc-cors`: CORS middleware integration for Connect-RPC to support browser clients using connectrpc.com/cors package
- `certificate-manager-integration`: Google-managed SSL certificate provisioning with automatic DNS validation and renewal
- `k8s-service-cross-namespace-routing`: HTTPRoute rules that route traffic across Kubernetes namespaces (gateway → backend)
- `argocd-gateway-deployment`: ArgoCD Application manifests for managing Gateway infrastructure via GitOps

### Modified Capabilities

- `backend-service-exposure`: Backend Service now discoverable from external Gateway via cross-namespace references

## Impact

- **Backend Code**: Add connectrpc.com/cors package, implement CORS middleware, add CORS_ALLOWED_ORIGINS environment variable
- **k8s Manifests** (cloud-provisioning): New `gateway` namespace with Gateway, HTTPRoute, and Policy resources
- **Infrastructure**: GKE Gateway (Global External ALB), Certificate Manager resources, DNS A record
- **Dependencies**: connectrpc.com/cors Go package (new), Cloud SQL unchanged, GKE cluster already in place
- **Cost**: +$97/month for Global ALB + Certificate Manager (dev environment, 0 RPS)
- **Breaking Changes**: None. Service remains accessible internally; only gains external exposure.
