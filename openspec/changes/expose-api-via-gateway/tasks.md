## 0. DNS Infrastructure (cloud-provisioning repo, Pulumi)

Configure hybrid DNS architecture: Cloudflare DNS for production (`liverty-music.app`, Proxy OFF) + Cloud DNS for dev environment (`dev.liverty-music.app`) via subdomain delegation. This is **Pulumi automation only** (no manual registrar updates).

### 0A. Pulumi Code Updates (cloud-provisioning repo)

- [x] 0.1 Extend GcpConfig interface with domain configuration
  - File: `src/gcp/components/project.ts`
  - Update: `GcpConfig` interface to include:
    ```typescript
    domains?: {
      publicDomain: string  // e.g., "liverty-music.app"
    }
    ```
  - Verify: TypeScript compilation succeeds

- [x] 0.2 Update NetworkComponent to accept and create public DNS zone
  - File: `src/gcp/components/network.ts`
  - Update: `NetworkComponentArgs` interface to include `publicDomain?: string`
  - Add: Public DNS zone creation:
    ```typescript
    if (args.publicDomain) {
      this.publicZone = new gcp.dns.ManagedZone('liverty-music-zone', {
        name: 'liverty-music-zone',
        dnsName: `${args.publicDomain}.`,
        visibility: 'public',
        description: 'Public zone for liverty-music.app'
      })
    }
    ```
  - Export: `this.publicZoneNameservers` from public zone for manual registrar step

- [x] 0.3 Update Gcp class to pass domain config to NetworkComponent
  - File: `src/gcp/index.ts`
  - Update: NetworkComponent instantiation to pass `publicDomain` from gcpConfig
  - Export: `publicZoneNameservers` output for reference
  - Verify: `npm run typecheck` passes

- [x] 0.4 Add Cloudflare provider integration
  - File: `cloud-provisioning/package.json`
  - Command: `npm install @pulumi/cloudflare`
  - Verify: `package.json` includes `@pulumi/cloudflare` dependency

- [x] 0.5 Create Cloudflare configuration interface
  - File: `src/cloudflare/config.ts` (already exists)
  - Verify: `CloudflareConfig` interface includes `apiToken` and `zoneId` fields
  - Note: This file was created in previous tasks

- [x] 0.6 Create Cloudflare DNS component for subdomain delegation
  - File: `src/cloudflare/components/dns-subdomain-delegation.ts` (new file)
  - Implement: Component that creates NS record for dev subdomain delegation
  - Input: `subdomain` (e.g., "dev"), `nameservers` (Cloud DNS nameservers from GCP)
  - Output: NS record pointing `dev.liverty-music.app` to Google nameservers

- [x] 0.7 Configure Pulumi ESC (cloud-provisioning/dev environment)
  - Access: Pulumi ESC web console or CLI (already configured)
  - Verify: ESC environment includes `cloudflare:apiToken` and `cloudflare:zoneId`
  - Note: Verified by user

- [x] 0.8 Update main Pulumi stack to integrate Cloudflare + Cloud DNS
  - File: `src/gcp/components/network.ts`
  - Update: Added Cloudflare provider and NS record creation
  - Update: Integrated Phase 1 (Certs, IP) into `NetworkComponent`
  - Verify: `npm run build` succeeds

- [x] 0.9 Run Pulumi up to provision DNS infrastructure
  - Command: `cd cloud-provisioning && pulumi stack select dev && pulumi up`
  - Review: Plan shows:
    - Cloud DNS zone creation for `dev.liverty-music.app`
    - Cloudflare NS record creation for subdomain delegation
  - Status: Completed by user

- [x] 0.10 Verify subdomain delegation
  - Command: `node -e 'require("dns").resolveNs("dev.liverty-music.app", (err, addr) => console.log(addr))'`
  - Result: Correctly points to Google nameservers (ns-cloud-aX.googledomains.com)
  - Status: Verified

---

## 1. GCP Certificate Setup (One-Time, Manual)

These steps provision TLS certificate infrastructure. Run once; results are reused across environments.

- [ ] 1.1 Create DNS Authorization in Certificate Manager
  - Command: `gcloud certificate-manager dns-authorizations create api-dns-auth --domain="api.dev.liverty-music.app"`
  - Verify: Check GCP Console → Certificate Manager → DNS Authorizations

- [ ] 1.2 Add CNAME record to Cloud DNS (dev subdomain)
  - Copy CNAME record from DNS Authorization output
  - Add to Cloud DNS zone for `dev.liverty-music.app` (via Pulumi or gcloud)
  - Verify: `nslookup <cname-record>` returns expected value

- [ ] 1.3 Create Google-managed certificate
  - Command: `gcloud certificate-manager certificates create api-cert --domains="api.dev.liverty-music.app" --dns-authorizations="api-dns-auth"`
  - Verify: Wait 5-10 minutes for certificate issuance
  - Command: `gcloud certificate-manager certificates describe api-cert --format="table(name,state)"`

- [ ] 1.4 Create Certificate Map
  - Command: `gcloud certificate-manager maps create api-cert-map`
  - Verify: `gcloud certificate-manager maps list`

- [ ] 1.5 Add certificate to Certificate Map
  - Command: `gcloud certificate-manager maps entries create api-entry --map="api-cert-map" --certificates="api-cert" --hostname="api.dev.liverty-music.app"`
  - Verify: `gcloud certificate-manager maps describe api-cert-map`

- [ ] 1.6 Reserve static IP address
  - Command: `gcloud compute addresses create api-static-ip --global`
  - Save the IP address (e.g., 35.X.X.X)
  - Verify: `gcloud compute addresses describe api-static-ip --global`

- [ ] 1.7 Add A record to Cloud DNS (dev subdomain)
  - Create A record in Cloud DNS zone for `dev.liverty-music.app`: `api.dev.liverty-music.app` → `<STATIC_IP>`
  - Can be done via Pulumi or gcloud: `gcloud dns record-sets create api.dev.liverty-music.app --zone=dev-liverty-music-zone --type=A --ttl=300 --rrdatas=<STATIC_IP>`
  - Wait for DNS propagation (5-30 minutes)
  - Verify: `nslookup api.dev.liverty-music.app` returns static IP

---

## 2. Backend Application Changes (backend repo)

Implement CORS middleware and environment configuration.

- [x] 2.1 Add connectrpc.com/cors dependency to go.mod
  - File: `backend/go.mod`
  - Command: `go get connectrpc.com/cors`
  - Verify: `grep connectrpc.com/cors go.mod` shows latest version

- [x] 2.2 Create CORS middleware file
  - File: `backend/internal/infrastructure/server/cors.go`
  - Implement: `NewCORSMiddleware()` function using `connectrpc.com/cors`
  - Include: `AllowedOrigins` from env var, `connectcors.AllowedMethods()`, `connectcors.AllowedHeaders()`, `connectcors.ExposedHeaders()`
  - Add: `Authorization` to allowed headers for future authentication

- [x] 2.3 Integrate CORS middleware into Connect server
  - File: `backend/internal/infrastructure/server/connect.go`
  - Update: `NewConnectServer()` to wrap mux with CORS middleware
  - Example: `handler := corsMiddleware(mux)`

- [x] 2.4 Add CORS_ALLOWED_ORIGINS to config
  - File: `backend/pkg/config/config.go`
  - Add field: `CORSAllowedOrigins string` to `Config` struct
  - Update: Kustomize ConfigMap generator to populate from env

- [x] 2.5 Add CORS validation at startup
  - File: `backend/cmd/server/main.go` or `internal/bootstrap/bootstrap.go`
  - Log warning if `CORS_ALLOWED_ORIGINS` not set or empty
  - Example: Log "⚠️  CORS not configured, browser requests will fail"

- [ ] 2.6 Test CORS locally
  - Command: `go run ./cmd/server`
  - Test CORS preflight: `curl -X OPTIONS http://localhost:8080/liverty_music.rpc.artist.v1.ArtistService/Search -H "Origin: http://localhost:5173" -v`
  - Verify: Response includes `Access-Control-Allow-Origin` header

---

## 4. Kubernetes Manifests (cloud-provisioning repo)

Create k8s resources following Kustomize structure.

### 3A. Cluster-Level Resources

- [x] 4.1 Update cluster/namespaces.yaml
  - File: `k8s/cluster/namespaces.yaml`
  - Add: `gateway` namespace definition (copy from backend ns, rename)
  - Verify: `kubectl apply -f k8s/cluster/namespaces.yaml --dry-run=client -o yaml`

### 3B. Gateway Namespace Resources

- [x] 3.2 Create gateway namespace directory structure
  - Directories:
    - `k8s/namespaces/gateway/base/`
    - `k8s/namespaces/gateway/overlays/dev/`

- [x] 3.3 Create Gateway resource
  - File: `k8s/namespaces/gateway/base/gateway.yaml`
  - Include:
    - `spec.gatewayClassName: gke-l7-global-external-managed`
    - `metadata.annotations["networking.gke.io/certmap"]: "api-cert-map"`
    - HTTPS listener (port 443, TLS mode: Terminate)
    - HTTP listener (port 80)
    - `allowedRoutes.namespaces.from: All`

- [x] 3.4 Create HTTPRoute for API
  - File: `k8s/namespaces/gateway/base/httproute-api.yaml`
  - Include:
    - `spec.parentRefs`: Gateway external-gateway
    - `spec.hostnames`: ["api.liverty-music.app"]
    - `spec.rules.backendRefs`: name: server, namespace: backend, port: 8080
    - Path matching: `/` (prefix)

- [x] 3.5 Create HTTPRoute for HTTP→HTTPS redirect
  - File: `k8s/namespaces/gateway/base/httproute-redirect.yaml`
  - Include:
    - Parent: HTTP listener (port 80)
    - Filter: RequestRedirect to HTTPS with status 301

- [x] 3.6 Create GCPGatewayPolicy
  - File: `k8s/namespaces/gateway/base/gateway-policy.yaml`
  - Include:
    - `spec.default.allowGlobalAccess: true`
    - Target: external-gateway
    - (Optional: `sslPolicy` if custom SSL policy created)

- [x] 3.7 Create base kustomization for gateway
  - File: `k8s/namespaces/gateway/base/kustomization.yaml`
  - Include:
    - Resources: gateway.yaml, httproute-api.yaml, httproute-redirect.yaml, gateway-policy.yaml
    - Namespace: gateway
    - Labels: app: gateway-ingress

- [x] 3.8 Create dev overlay for gateway
  - File: `k8s/namespaces/gateway/overlays/dev/kustomization.yaml`
  - Include:
    - Bases: ../../base
    - Namespace: gateway
    - (Optional patches for dev-specific settings)

### 3C. Backend Namespace Policies

- [x] 3.9 Create HealthCheckPolicy for backend Service
  - File: `k8s/namespaces/backend/base/policies/healthcheck-policy.yaml`
  - Include:
    - `spec.default.config.type: GRPC`
    - `spec.default.config.grpcHealthCheck.port: 8080`
    - `spec.default.checkIntervalSec: 15`, `timeoutSec: 5`
    - Target: Service server in backend namespace

- [x] 3.10 Create GCPBackendPolicy for backend Service
  - File: `k8s/namespaces/backend/base/policies/backend-policy.yaml`
  - Include:
    - `spec.default.timeoutSec: 30`
    - `spec.default.connectionDraining.drainingTimeoutSec: 60`
    - `spec.default.logging.enabled: true`, `sampleRate: 1000000`
    - Target: Service server in backend namespace

- [x] 3.11 Create kustomization for backend policies
  - File: `k8s/namespaces/backend/base/policies/kustomization.yaml`
  - Resources: healthcheck-policy.yaml, backend-policy.yaml
  - Namespace: backend

- [x] 3.12 Update backend base kustomization
  - File: `k8s/namespaces/backend/base/kustomization.yaml`
  - Update resources to include: `policies/kustomization.yaml`

- [x] 3.13 Verify backend Service has appProtocol
  - File: `k8s/namespaces/backend/base/backend-app/service.yaml`
  - Ensure: `ports[0].appProtocol: kubernetes.io/h2c`
  - Verify: `kubectl apply -f k8s/namespaces/backend/base/backend-app/service.yaml --dry-run=client`

### 3D. Backend Dev Overlay

- [x] 3.14 Update backend dev overlay with cost optimization
  - File: `k8s/namespaces/backend/overlays/dev/kustomization.yaml`
  - Add patch for Deployment:
    - `spec.replicas: 1`
    - Resources: `requests: {cpu: 100m, memory: 256Mi}`
    - Resources: `limits: {cpu: 500m, memory: 512Mi}`

---

## 5. ArgoCD Applications (cloud-provisioning repo)

Create GitOps Application resources for automated deployment.

- [x] 4.1 Create cluster ArgoCD Application
  - File: `k8s/argocd-apps/dev/cluster-app.yaml` (Confirmed as `cluster.yaml`)
  - Include:
    - `source.path: k8s/cluster`
    - `destination.namespace: kube-system` (Note: Uses `argocd` ns for management)
    - `syncPolicy.automated.prune: true`

- [x] 4.2 Create gateway ArgoCD Application
  - File: `k8s/argocd-apps/dev/gateway-app.yaml` (Confirmed as `gateway.yaml`)
  - Include:
    - `source.path: k8s/namespaces/gateway/overlays/dev`
    - `destination.namespace: gateway`
    - `syncPolicy.automated.selfHeal: true`
    - `syncPolicy.syncOptions: [CreateNamespace=true]`

- [x] 4.3 Create/update backend ArgoCD Application
  - File: `k8s/argocd-apps/dev/backend-app.yaml` (Confirmed as `backend.yaml`)
  - Include:
    - `source.path: k8s/namespaces/backend/overlays/dev`
    - `destination.namespace: backend`
    - `syncPolicy.automated.prune: true`
    - `syncPolicy.syncOptions: [CreateNamespace=true]`

- [ ] 4.4 Commit and push cloud-provisioning changes
  - Commit message: `feat: add gateway infrastructure and backend policies for external API exposure (#expose-api-via-gateway)`
  - Verify: All manifests committed, `git status` is clean

---

## 6. Deployment via ArgoCD

Deploy infrastructure step-by-step using ArgoCD for safety.

- [ ] 5.1 Apply cluster-app to create namespaces
  - Command: `argocd app create cluster --repo <repo-url> --path k8s/cluster --dest-namespace kube-system --project default` (or update if exists)
  - Command: `argocd app sync cluster --wait`
  - Verify: `kubectl get namespaces | grep -E "gateway|backend"`

- [ ] 5.2 Apply gateway-app to create LB infrastructure
  - Command: `argocd app create gateway --repo <repo-url> --path k8s/namespaces/gateway/overlays/dev --dest-namespace gateway --project default` (or update)
  - Command: `argocd app sync gateway --wait`
  - Verify: `kubectl get gateway -n gateway`, `kubectl get httproute -n gateway`

- [ ] 5.3 Apply backend-app to create updated Service and Policies
  - Command: `argocd app create backend --repo <repo-url> --path k8s/namespaces/backend/overlays/dev --dest-namespace backend --project default` (or update)
  - Command: `argocd app sync backend --wait`
  - Verify: `kubectl get service server -n backend`, `kubectl get healthcheckpolicy -n backend`

- [ ] 5.4 Verify Gateway provisioning
  - Command: `kubectl get gateway -n gateway -o wide`
  - Expected: Status shows PROGRAMMED=true, IP address assigned
  - Note: Takes 2-5 minutes for GCP to provision ALB

- [ ] 5.5 Verify DNS resolution
  - Command: `nslookup api.liverty-music.app`
  - Verify: Returns static IP address reserved in step 1.6

---

## 7. Testing & Verification

Validate entire infrastructure end-to-end.

- [ ] 6.1 Test HTTP→HTTPS redirect
  - Command: `curl -v http://api.liverty-music.app` (or use curl -L to follow)
  - Verify: Receives 301 redirect to https://api.liverty-music.app
  - Verify: No certificate error on HTTPS connection

- [ ] 6.2 Test TLS certificate validity
  - Command: `openssl s_client -connect api.liverty-music.app:443 -showcerts`
  - Verify: Certificate CN matches api.liverty-music.app
  - Verify: Certificate is issued by Google CA

- [ ] 6.3 Test CORS preflight for API
  - Command: `curl -X OPTIONS https://api.liverty-music.app/liverty_music.rpc.artist.v1.ArtistService/SearchArtists -H "Origin: https://liverty-music.app" -v`
  - Verify: Response code 200
  - Verify: Response includes `Access-Control-Allow-Origin: https://liverty-music.app`
  - Verify: Response includes Connect-specific headers in Allow-Headers

- [ ] 6.4 Test actual API call from curl
  - Command: `curl -X POST https://api.liverty-music.app/liverty_music.rpc.artist.v1.ArtistService/SearchArtists -H "Content-Type: application/json" -d '{"query":"test"}' -v`
  - Verify: Request reaches backend (no CORS errors)
  - Verify: Response includes proper status code

- [ ] 6.5 Test from browser (manual)
  - Open DevTools → Network tab
  - Navigate to frontend app (liverty-music.app)
  - Trigger API call from Aurelia 2 component
  - Verify: Request to api.liverty-music.app shows CORS headers
  - Verify: Response contains data (no CORS blocked error)

- [ ] 6.6 Verify backend pod health
  - Command: `kubectl get pods -n backend -o wide`
  - Verify: All pods show READY 1/1 and RUNNING
  - Command: `kubectl logs -n backend -f deployment/backend` (watch logs)
  - Verify: No CORS warnings in logs

- [ ] 6.7 Test failover (pod restart)
  - Command: `kubectl delete pod -n backend -l app=backend`
  - Verify: New pod starts
  - Verify: Gateway continues routing (health check updates)
  - Verify: API requests succeed without interruption

---

## 8. Documentation & Cleanup

Finalize implementation.

- [ ] 7.1 Document Open Questions answers
  - DNS provider: ___________
  - Frontend CORS origin(s): ___________
  - Monitoring setup: ___________
  - Backup strategy: ___________

- [ ] 7.2 Create runbook for operations
  - File: `docs/GATEWAY_OPERATIONS.md` (in cloud-provisioning or backend repo)
  - Include: How to update cert, troubleshoot Gateway, monitor costs

- [ ] 7.3 Verify no leftover resources
  - Command: `argocd app list` (all apps in Synced state)
  - Command: `kubectl get all -n gateway` (all expected resources present)
  - Command: `kubectl get all -n backend` (all expected resources present)

---

## Implementation Notes

**Prerequisite**: Phase 0 (Cloud DNS) must complete before Phase 1-8. DNS propagation (Phase 0.7) takes 5-30 minutes.

**Dependency Order**:
- **Phase 0**: Cloud DNS (Pulumi + manual registrar) — Prerequisite for all later phases
- **Phases 1-2**: GCP + Backend changes (can run in parallel)
- **Phases 3-5**: Kubernetes + ArgoCD (depends on backend code ready)
- **Phases 6-8**: Testing + documentation (final verification)

Within each phase, most tasks can be parallelized except where noted.

**Rollback**:
- Phase 0 (DNS): Remove A records from Cloud DNS zone, keep zone active for reuse
- Phases 1-5 (GCP/k8s/ArgoCD): Run `argocd app delete <app>` to remove resources. GCP Certificate remains for reuse.
- Phase 2 (Backend): Revert git commits, redeploy via ArgoCD

**Cost Monitoring**: After Phase 5 deployment, check GCP Console → Billing to see actual costs (may take 1-2 days for data to appear).
