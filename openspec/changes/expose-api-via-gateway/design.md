## Context

The backend service (Connect-RPC, port 8080) is deployed on GKE but lacks external exposure. The Aurelia 2 PWA frontend needs to call backend APIs via HTTPS from `liverty-music.app`.

**Current State:**
- Backend: Connect-RPC server (h2c support), running in `backend` namespace
- Cloud SQL: PostgreSQL with IAM auth + Private Service Connect
- Networking: No external load balancer or TLS termination
- k8s Config: Kustomize (base/overlays), managed via ArgoCD in cloud-provisioning repo

**Constraints:**
- Cost: Dev environment only ($97/month target)
- Domain: Use `api.liverty-music.app` subdomain
- Architecture: Separate Gateway (LB) management from app management (namespace-level separation)
- Certificate: Google-managed certificates via Certificate Manager

## Goals / Non-Goals

**Goals:**
1. Expose backend API on `api.liverty-music.app` with automatic TLS
2. Support CORS for browser clients (Aurelia 2)
3. Separate LB infrastructure (gateway namespace) from application (backend namespace)
4. Implement health checks using gRPC health protocol
5. Use GKE Gateway API (modern, cloud-native approach)
6. Integrate with ArgoCD for GitOps deployment
7. Enable future scaling (add new APIs without LB reconfiguration)

**Non-Goals:**
- Multi-region deployment (future consideration)
- gRPC-Web transcoding (Connect protocol handles browsers natively)
- Custom authentication/authorization at LB level (app-level concern)
- Cost optimization beyond dev environment (e.g., AlloyDB, reserved capacity)
- Production hardening (Cloud Armor, advanced monitoring setup)

## Decisions

### 1. **Namespace Separation: `gateway` + `backend` (Not Single Namespace)**

**Decision:** Create separate `gateway` namespace for LB infrastructure.

**Rationale:**
- Segregates concerns: LB management independent from app deployment
- Future-proof: Multiple backends (API v2, admin APIs) can share single Gateway
- Team scaling: Infrastructure team manages gateway ns, app team manages backend ns
- Clean boundaries for GitOps (separate ArgoCD Applications)

**Alternatives Considered:**
- Single namespace: Simpler initially, but couples LB to app lifecycle. Rejected.
- No namespace separation: Not possible—Gateway and HTTPRoute must be in same namespace.

### 2. **Certificate Binding: Annotation Method (Certificate Manager Map)**

**Decision:** Use `networking.gke.io/certmap` annotation instead of spec-based certificateRefs.

**Rationale:**
- Official GCP recommendation for Global External ALB (`gke-l7-global-external-managed`)
- Simpler: Certificate Manager handles auto-renewal, DNS auth
- Cleaner YAML: Single annotation vs. complex spec nesting
- Standard GKE pattern: Well-documented, widely used

**Spec:**
```yaml
metadata:
  annotations:
    networking.gke.io/certmap: "api-cert-map"
```

**Alternatives Considered:**
- Spec-based certificateRefs: More flexible but verbose. Only needed for edge cases.
- Self-signed certs: Development only, not suitable for production.

### 3. **Cross-Namespace Routing: HTTPRoute → backend Service**

**Decision:** HTTPRoute (gateway ns) references Service (backend ns) via explicit namespace field.

**Rationale:**
- Gateway allows `allowedRoutes.namespaces.from: All`
- HTTPRoute backendRefs includes namespace field: `namespace: backend`
- Clean separation without network policies

**Implementation:**
```yaml
# gateway/base/httproute-api.yaml
spec:
  backendRefs:
  - name: music-api
    namespace: backend      ← Explicit cross-namespace reference
    port: 8080
```

### 4. **CORS: Application-Level Middleware**

**Decision:** Implement CORS via `connectrpc.com/cors` package in Connect-RPC server.

**Rationale:**
- Connect protocol uses custom headers (Connect-Protocol-Version, Connect-Timeout-Ms)
- Load balancer cannot configure protocol-specific CORS rules
- connectrpc.com/cors provides correct header mapping
- Single source of truth for CORS policy

**Implementation:**
```go
import "connectrpc.com/cors"

opts := cors.Options{
    AllowedOrigins: strings.Split(os.Getenv("CORS_ALLOWED_ORIGINS"), ","),
    AllowedMethods: connectcors.AllowedMethods(),       // [GET, POST]
    AllowedHeaders: append(connectcors.AllowedHeaders(), "Authorization"),
    ExposedHeaders: connectcors.ExposedHeaders(),       // [Grpc-Status, etc]
    MaxAge: 7200,
}
```

**Env:** `CORS_ALLOWED_ORIGINS=https://liverty-music.app,http://localhost:5173`

### 5. **Health Checks: gRPC Protocol**

**Decision:** Use HealthCheckPolicy with gRPC health check protocol.

**Rationale:**
- Backend already implements `grpc.health.v1.Check` interface
- More accurate than HTTP health checks for gRPC/Connect services
- GKE HealthCheckPolicy natively supports gRPC type
- Port 8080 already has health endpoint

**Spec:**
```yaml
config:
  type: GRPC
  grpcHealthCheck:
    port: 8080
```

### 6. **Environment Strategy: Dev-Only Resources**

**Decision:** Create only `overlays/dev/` (no prod, staging). Estimated cost: $97/month.

**Rationale:**
- Service pre-launch: 0 RPS initially
- Cost optimization: Single Global ALB, single Pod replica
- Reduce maintenance: Fewer environments = fewer issues
- Migration path: Copy dev/ → prod/ when needed, customize overlay

**Cost Breakdown (Dev):**
- Cloud SQL (PostgreSQL): $60/mo
- Global ALB: $18/mo
- GKE Compute (100m CPU, 256Mi RAM): $3/mo
- DNS + Misc: $0.20/mo
- **Total: ~$97/month**

### 7. **DNS Architecture: Cloudflare for Production + Cloud DNS for Dev**

**Decision:** Use Cloudflare DNS for production domain (`liverty-music.app`) with Proxy OFF, and delegate dev subdomain (`dev.liverty-music.app`) to Cloud DNS via NS records.

**Rationale:**
- Domain purchased through Cloudflare Registrar (requires Cloudflare nameservers)
- Cloudflare Proxy OFF (DNS only) maintains Certificate Manager simplicity and avoids TLS termination complexity
- Dev environment isolation via subdomain delegation to Cloud DNS
- Production uses Cloudflare DNS directly for consistency with registrar

**Implementation:**
- **Production (via Pulumi Cloudflare provider):**
  - Manage Cloudflare DNS zone via `@pulumi/cloudflare` package
  - Configure Proxy OFF for all records (DNS only mode)
  - Create A record for `api.liverty-music.app` → static IP
  - Cloudflare ESC config: `cloudflare.apiToken`, `cloudflare.zoneId`

- **Dev Environment (via Cloud DNS subdomain delegation):**
  - Extend `GcpConfig` with `domains.publicDomain` field (set to `dev.liverty-music.app`)
  - Update `NetworkComponent` to create public managed zone for dev subdomain
  - Export Google nameservers for subdomain NS record
  - Create NS record in Cloudflare: `dev.liverty-music.app` → Google's 4 nameservers
  - Dev A record: `api.dev.liverty-music.app` → dev static IP (managed in Cloud DNS)

**No Manual Registrar Update:**
- Domain already registered at Cloudflare; nameservers remain Cloudflare's
- Only subdomain delegation via NS records (automated via Pulumi)

### 8. **GitOps: Three ArgoCD Applications**

**Decision:** Create three separate ArgoCD Applications.

**Rationale:**
- `cluster-app`: Manages cluster-level resources (namespaces)
- `gateway-app`: Manages LB infrastructure (independent lifecycle)
- `backend-app`: Manages application (deployment, config)

**Decoupling Benefits:**
- Gateway config can change without redeploying backend
- Backend updates don't require LB recreation
- Clear responsibility boundaries

## Risks / Trade-offs

### Risk 1: Cross-Namespace Routing Adds Complexity
**Risk:** HTTPRoute referencing backend Service requires namespace awareness.
**Mitigation:** Document in comments, enforce via code review. Explicit namespace references are clearer than implicit discovery.

### Risk 2: CORS Configuration in Two Places (App + Env)
**Risk:** If env var not set, CORS fails silently.
**Mitigation:** Default origins in code to empty (fail-closed), validate at startup, log warning if CORS_ALLOWED_ORIGINS not set.

### Risk 3: Certificate Auto-Renewal (Google-Managed)
**Risk:** Certificate Manager handles renewal automatically—hidden complexity.
**Mitigation:** Monitor Certificate Manager dashboard, set up alerts for cert expiry (unlikely but good practice).

### Risk 4: Single Pod in Dev
**Risk:** Single backend pod means zero availability during updates.
**Mitigation:** Acceptable for dev (pre-launch). Upgrade to 2+ replicas before prod.

### Risk 5: Global ALB Cost Grows with Traffic
**Risk:** At 1000 RPS avg, cost jumps to ~$3,300/mo.
**Mitigation:** Cost is feature, not bug. Scale happens when product succeeds. Monitor cost via GCP dashboards.

## Migration Plan

**Phase 0: DNS Infrastructure (Cloudflare + Cloud DNS Subdomain Delegation)**
- Update cloud-provisioning Pulumi code: extend GcpConfig, update NetworkComponent, add Cloudflare provider
- Add Pulumi ESC config: `cloudflare.apiToken`, `cloudflare.zoneId`, `gcp.domains.publicDomain: "dev.liverty-music.app"`
- Run `pulumi up` →
  - Cloud DNS zone provisioned for `dev.liverty-music.app`, outputs Google nameservers
  - Cloudflare NS record created: `dev.liverty-music.app` → Google nameservers (subdomain delegation)
- Verify DNS delegation: `dig NS dev.liverty-music.app` returns Google nameservers
- No manual registrar update needed (domain already at Cloudflare)

**Step 1: GCP Setup (Manual, One-time)**
```bash
# DNS Authorization
gcloud certificate-manager dns-authorizations create api-dns-auth \
    --domain="api.liverty-music.app"

# Get CNAME record, add to DNS provider (external)

# Create Certificate
gcloud certificate-manager certificates create api-cert \
    --domains="api.liverty-music.app" \
    --dns-authorizations="api-dns-auth"

# Create Certificate Map
gcloud certificate-manager maps create api-cert-map
gcloud certificate-manager maps entries create api-entry \
    --map="api-cert-map" \
    --certificates="api-cert" \
    --hostname="api.liverty-music.app"

# Reserve Static IP
gcloud compute addresses create api-static-ip \
    --global

# Add A record to DNS provider: api.liverty-music.app → <STATIC_IP>
```

**Step 2: Backend Changes (backend repo)**
- Add `connectrpc.com/cors` to go.mod
- Implement CORS middleware in server.go
- Add CORS_ALLOWED_ORIGINS to config.go
- Test locally with curl/postman

**Step 3: k8s Manifests (cloud-provisioning repo)**
- Update cluster/namespaces.yaml (add gateway ns)
- Create gateway/base/ resources
- Create backend/base/policies/ resources
- Create ArgoCD Applications (cluster, gateway, backend)
- Validate with dry-run: `kubectl apply -f ... --dry-run`

**Step 4: Deploy via ArgoCD**
- Apply cluster-app → creates namespaces
- Apply gateway-app → creates Gateway, HTTPRoute, Policies
- Apply backend-app → creates Deployment, Service, Policies
- Verify: HTTPRoute status, gateway IP, curl test

**Step 5: End-to-End Test**
```bash
# Test HTTP→HTTPS redirect
curl -v http://api.liverty-music.app

# Test CORS preflight
curl -X OPTIONS https://api.liverty-music.app/liverty_music.rpc.artist.v1.ArtistService/Search \
  -H "Origin: https://liverty-music.app" -v

# Test actual RPC call (from browser)
# In DevTools console:
fetch('https://api.liverty-music.app/liverty_music.rpc.artist.v1.ArtistService/SearchArtists', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({...})
})
```

**Rollback:** Remove ArgoCD Applications, delete gateway namespace. Backend remains unchanged.

## Open Questions

1. **Frontend CORS Origins:** Exact production domain for frontend? (liverty-music.app or subdomain?)
2. **Monitoring:** Should we set up Cloud Logging for Gateway metrics now or later?
3. **Future Scale:** When traffic arrives, which env vars/configs will change? (Document for ops team)
4. **Backup Strategy:** Cloud SQL backups already configured? Retention policy?
