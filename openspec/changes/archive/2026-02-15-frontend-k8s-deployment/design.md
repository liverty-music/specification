## Context

The Liverty Music platform currently has a fully operational backend (Go Connect-RPC server) deployed on GKE using ArgoCD GitOps workflow, but the Aurelia 2 frontend SPA is not deployed anywhere. The existing infrastructure includes:

- **GKE cluster** with ArgoCD for continuous deployment
- **Gateway API** (GKE L7 GCLB) with TLS cert management
- **Backend namespace** serving gRPC at `api.dev.liverty-music.app`
- **Artifact Registry** for container images
- **GitHub Actions** for backend CI/CD

The frontend is a Vite-built Aurelia 2 SPA that produces static assets (HTML, JS, CSS) requiring a web server for hosting and client-side routing support.

## Goals / Non-Goals

**Goals:**
- Deploy frontend to GKE using the same GitOps pattern as backend
- Serve static assets with efficient caching and SPA routing fallback
- Automate container builds on merge to main
- Use modern, minimal tooling aligned with 2026 best practices
- Maintain consistency with existing infrastructure patterns

**Non-Goals:**
- CDN edge delivery (Cloudflare/Fastly) - can be added later if needed
- Production deployment automation (remains manual via GitHub releases)
- Multi-region or geo-distributed hosting
- Server-side rendering (SSR) or hybrid rendering

## Decisions

### D1: Web Server - Caddy vs Nginx

**Decision**: Use Caddy 2

**Rationale**:
- **Simplicity**: 4-line Caddyfile vs 10+ line nginx.conf for SPA routing
- **Container-native**: Official `caddy:2-alpine` image (~50MB)
- **Modern**: Automatic HTTPS, built for cloud-native deployments
- **SPA-friendly**: `try_files {path} /index.html` is a one-liner
- **2026 trend**: Gaining adoption for new projects vs Nginx

**Alternatives considered**:
- Nginx: More mature, better for high-scale (50k+ req/s), but overkill for dev and adds config complexity
- Apache: Process-based model, not container-optimized, avoid

### D2: Build Strategy - Multi-stage Dockerfile

**Decision**: Multi-stage Docker build (Node builder → Caddy runtime)

**Rationale**:
- **Security**: Final image contains only runtime dependencies (no Node, npm, source code)
- **Size**: ~50MB final image vs ~1GB if Node included
- **Reproducibility**: Vite build happens in controlled container environment
- **Best practice**: Standard pattern for frontend container builds

**Build stages**:
1. `node:22-alpine` - Install deps, run `npm run build`, produce `/dist`
2. `caddy:2-alpine` - Copy `/dist` and `Caddyfile`, expose port 80

### D3: Deployment Pattern - GitOps with ArgoCD

**Decision**: Follow existing backend pattern (ArgoCD Application + Kustomize overlays)

**Rationale**:
- **Consistency**: Same workflow as backend (cloud-provisioning repo, ArgoCD sync)
- **Proven**: Already working for backend deployments
- **Auditability**: All changes tracked in Git
- **No new tools**: Leverages existing cluster infrastructure

**Structure**:
```
cloud-provisioning/k8s/
├── argocd-apps/dev/frontend.yaml
└── namespaces/frontend/
    ├── base/ (deployment, service, httproute, Caddyfile ConfigMap)
    └── overlays/dev/ (hostname patches)
```

### D4: Domain - dev.liverty-music.app

**Decision**: Use `dev.liverty-music.app` (not `app.dev.liverty-music.app`)

**Rationale**:
- User-specified requirement
- Shorter, cleaner domain
- Consistent with existing pattern (`api.dev.liverty-music.app`)

**DNS/TLS**: Requires adding `dev.liverty-music.app` to existing `api-gateway-cert-map` and DNS records

### D5: CI/CD - GitHub Actions for Image Builds

**Decision**: Automated image builds on push to main, manual production releases

**Rationale**:
- **Consistency**: Mirrors backend CI pattern
- **Dev velocity**: Auto-deploy to dev on merge
- **Production safety**: Manual release process prevents accidental deploys

**Workflow**: `.github/workflows/push-image.yaml`
- Trigger: `push` to `main` branch
- Build: Multi-stage Docker build
- Push: Tag with commit SHA to Google Artifact Registry
- ArgoCD: Polls GAR for new tags (or uses Image Updater for auto-sync)

### D6: Resource Allocation

**Decision**: Start with minimal resources, scale based on actual usage

**Initial resources**:
- 1 replica (scale manually if needed)
- CPU: 50m request / 200m limit
- Memory: 64Mi request / 128Mi limit
- Spot VMs: Follow backend pattern (cost optimization)

**Rationale**: Static file serving has minimal resource needs; over-provisioning wastes money

## Risks / Trade-offs

### R1: No CDN - Slower global access
**Mitigation**: GKE L7 GCLB provides global load balancing. Add Cloudflare later if latency becomes an issue.

### R2: Single replica - No HA during pod restarts
**Mitigation**: Static assets load quickly (< 1s restart). If uptime becomes critical, scale to 2+ replicas.

### R3: Spot VMs - Occasional pod evictions
**Mitigation**: ArgoCD auto-heals; frontend is stateless so restarts are safe. Monitor eviction rates.

### R4: Manual DNS/cert setup required
**Mitigation**: Document DNS record and cert-map update steps in tasks. One-time setup per environment.

### R5: Image tag updates require manual commit (if not using Image Updater)
**Mitigation**: Align with backend's upcoming Image Updater automation (change: `automate-dev-deployment`). Manually update image tags in overlay until then.

## Migration Plan

### Deployment steps:
1. **Prepare DNS/TLS**: Add `dev.liverty-music.app` to cert-map and DNS
2. **Deploy ArgoCD app**: Apply `k8s/argocd-apps/dev/frontend.yaml`
3. **Sync manifests**: ArgoCD pulls from cloud-provisioning main
4. **Build initial image**: Run CI workflow manually or merge Dockerfile PR
5. **Verify**: Access `https://dev.liverty-music.app`, check SPA routing

### Rollback:
- Delete ArgoCD Application: `kubectl delete app frontend -n argocd`
- Remove frontend namespace: `kubectl delete ns frontend`
- Revert cloud-provisioning commits

### Success criteria:
- Frontend accessible at `https://dev.liverty-music.app`
- Client-side routes (e.g., `/users`, `/concerts`) load index.html
- Static assets served with correct caching headers
- ArgoCD shows healthy sync status

## Open Questions

None - design is complete and ready for implementation.
