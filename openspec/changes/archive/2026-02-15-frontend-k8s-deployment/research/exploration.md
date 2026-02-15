# Frontend K8s Hosting Exploration

**Date**: 2026-02-14
**Topic**: Hosting Aurelia 2 frontend web app on Kubernetes

---

## Current Infrastructure

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GKE CLUSTER (dev)                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ ARGOCD (GitOps - self-managing)                              │ │
│  │ Watches: cloud-provisioning repo (main)                      │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ GATEWAY NAMESPACE                                            │ │
│  │ - GKE Gateway API (L7 GCLB)                                  │ │
│  │ - Static IP: api-gateway-static-ip                           │ │
│  │ - Cert Manager: api-gateway-cert-map                         │ │
│  │ - HTTPS (443)                                                │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                        │                                            │
│                        │                                            │
│  ┌─────────────────────▼──────────────────────────────────────┐   │
│  │ BACKEND NAMESPACE                                           │   │
│  │ HTTPRoute: api.dev.liverty-music.app                        │   │
│  │ - Go Connect-RPC server                                     │   │
│  │ - gRPC health checks                                        │   │
│  │ - 1 replica (spot VMs)                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ FRONTEND NAMESPACE                                           │   │
│  │ ❌ NOT DEPLOYED                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## What You're Building

- **Frontend**: Aurelia 2 SPA
- **Build tool**: Vite
- **Build output**: Static HTML + JS/CSS bundles
- **Routing**: Client-side (needs fallback to index.html)

## The Core Question

Where should static files live in 2026? Three fundamentally different approaches:

```
HOSTING SPECTRUM
════════════════════════════════════════════════════

    Self-Host               Hybrid                Pure CDN
        │                      │                      │
        ▼                      ▼                      ▼
   ┌──────────┐          ┌──────────┐          ┌──────────┐
   │K8s+Web   │          │ K8s +    │          │ CDN      │
   │Server    │          │ CDN Edge │          │ Origin   │
   │          │          │          │          │          │
   │Full      │          │Cache     │          │No K8s    │
   │Control   │          │Layer     │          │Deploy    │
   └──────────┘          └──────────┘          └──────────┘
        │                      │                      │
   Fits your              Best of both          Different
   infra today            worlds                paradigm
```

---

## Option 1: Self-Host on K8s (RECOMMENDED)

This fits naturally into your existing GitOps flow:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SELF-HOST ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  GKE Gateway API    │
                    │  (L7 GCLB)          │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
         ┌──────────▼──────────┐  ┌──────▼───────────┐
         │ HTTPRoute           │  │ HTTPRoute        │
         │ api.dev...          │  │ app.dev...       │
         └──────────┬──────────┘  └──────┬───────────┘
                    │                     │
         ┌──────────▼──────────┐  ┌──────▼───────────┐
         │ BACKEND             │  │ FRONTEND         │
         │ - Go Server         │  │ - Caddy/Nginx    │
         │ - gRPC              │  │ - Static files   │
         │                     │  │ - SPA routing    │
         └─────────────────────┘  └──────────────────┘
```

### Web Server: 2026 Best Practices

Based on current trends, here's the landscape:

| Server | Best For | Why 2026 |
|--------|----------|----------|
| **Caddy** | Modern SPAs, small teams | Auto-HTTPS, dead simple config, built for containers |
| **Nginx** | High traffic, enterprise | Proven at scale, lowest latency, industry standard |
| **Apache** | Legacy compat | Process-based (slow), not containerized, avoid |

**For your use case**: **Caddy** is recommended.

#### Why Caddy?

1. **Automatic HTTPS** - Zero config TLS (though GKE Gateway handles this)
2. **SPA-friendly routing** - One-liner for fallback to index.html
3. **Minimal config** - Perfect for GitOps (tiny Caddyfile)
4. **Container-native** - Official images, tiny footprint
5. **2026 trend** - Gaining massive traction vs Nginx for new projects

Compare configurations:

**Caddy**:
```caddyfile
:80 {
    root * /srv
    file_server
    try_files {path} /index.html
}
```

**Nginx**:
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Caddy wins on simplicity.

### Implementation Steps (Self-Host)

```
BUILD PIPELINE
══════════════════════════════════════════════════════

┌────────────────┐
│ 1. Build Stage │  Vite builds to /dist
│ ┌────────────┐ │  • index.html
│ │ npm run    │ │  • assets/*.js
│ │ build      │ │  • assets/*.css
│ └────────────┘ │  • favicon, etc.
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ 2. Containerize│  Multi-stage Dockerfile
│ ┌────────────┐ │  FROM caddy:2-alpine
│ │ Docker     │ │  COPY dist/ /srv
│ │ build      │ │  COPY Caddyfile /etc/caddy/
│ └────────────┘ │  EXPOSE 80
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ 3. Push to GAR │  Artifact Registry
│ ┌────────────┐ │  region-docker.pkg.dev/
│ │ Docker     │ │    project/repo/frontend:tag
│ │ push       │ │
│ └────────────┘ │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ 4. GitOps Sync │  ArgoCD watches
│ ┌────────────┐ │  cloud-provisioning/k8s/
│ │ ArgoCD     │ │    namespaces/frontend/
│ │ deploys    │ │  Auto-deploys to GKE
│ └────────────┘ │
└────────────────┘
```

### What You Need to Create

```
REPOSITORY STRUCTURE
════════════════════════════════════════════════════

cloud-provisioning/
├── k8s/
│   ├── argocd-apps/dev/
│   │   └── frontend.yaml           ← NEW: ArgoCD Application
│   │
│   └── namespaces/frontend/        ← NEW: Namespace
│       ├── base/
│       │   ├── kustomization.yaml
│       │   ├── deployment.yaml     # Caddy container
│       │   ├── service.yaml        # ClusterIP service
│       │   ├── httproute.yaml      # app.dev.liverty-music.app
│       │   └── configmap.yaml      # Caddyfile (optional)
│       │
│       └── overlays/dev/
│           ├── kustomization.yaml
│           └── httproute_patch.yaml # Domain override

frontend/
├── Dockerfile                       ← NEW: Multi-stage build
├── Caddyfile                        ← NEW: Web server config
└── .github/workflows/
    └── build.yaml                   ← NEW: CI pipeline
```

### Dockerfile Example (Multi-stage)

```dockerfile
# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM caddy:2-alpine
COPY --from=builder /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
EXPOSE 80
```

---

## Option 2: Hybrid (K8s + CDN Edge)

Add Cloudflare in front of your K8s deployment:

```
┌───────────────────────────────────────────────────────┐
│                 HYBRID ARCHITECTURE                   │
└───────────────────────────────────────────────────────┘

Internet
   │
   ▼
┌──────────────────┐
│ Cloudflare CDN   │  Global edge network
│ - Cache static   │  app.dev.liverty-music.app
│ - DDoS protect   │
│ - WAF            │
└────────┬─────────┘
         │ (cache miss)
         ▼
┌──────────────────┐
│ GKE Gateway API  │  Origin server
│                  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ K8s Frontend     │  Caddy serving static files
│ (Origin)         │
└──────────────────┘
```

### Pros/Cons

**Pros**:
- Faster global delivery (edge caching)
- Free DDoS protection (Cloudflare)
- Reduced GKE egress costs
- Built-in WAF

**Cons**:
- Another layer to manage
- Cache invalidation complexity
- Cloudflare config drift from GitOps

**When to use**: High global traffic, need DDoS protection, cost-sensitive egress

---

## Option 3: Pure CDN (Cloudflare Pages / Vercel / Netlify)

Skip K8s entirely for frontend:

```
┌───────────────────────────────────────────────────────┐
│                 PURE CDN ARCHITECTURE                 │
└───────────────────────────────────────────────────────┘

┌────────────────┐
│ Frontend Repo  │  github.com/liverty-music/frontend
│ (main branch)  │
└────────┬───────┘
         │ (push)
         ▼
┌────────────────┐
│ Cloudflare     │  Auto-build & deploy
│ Pages          │  Global edge network
│                │  app.dev.liverty-music.app
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Backend API    │  api.dev.liverty-music.app
│ (K8s)          │  CORS-enabled
└────────────────┘
```

### Pros/Cons

**Pros**:
- Zero infrastructure management
- Instant global CDN
- Free tier (Cloudflare Pages)
- Preview deployments
- Atomic deployments

**Cons**:
- **Breaks GitOps paradigm** (not in your k8s repo)
- Different deployment model than backend
- Less control
- Vendor lock-in

**When to use**: Rapid iteration, small team, willing to split infra patterns

---

## Recommendation

Given your context:

1. ✅ **Already using GKE + ArgoCD GitOps**
2. ✅ **Active change for automating dev deployments**
3. ✅ **Backend follows k8s-native pattern**
4. ✅ **Team comfortable with k8s**

→ **Option 1: Self-Host on K8s with Caddy**

### Why?

- **Consistency**: Frontend deployment mirrors backend (same GitOps flow)
- **Simplicity**: Everything in one repo, one cluster, one CD system
- **Control**: Full visibility and debugging with kubectl
- **2026-ready**: Caddy is modern, minimal, and trending
- **Cost**: No CDN fees for dev (GKE handles HA)

### Later: Add CDN if needed

You can always add Cloudflare later as Option 2 (hybrid) once you have traffic data. No need to over-engineer day 1.

---

## Next Steps

1. **Create a change**: `/opsx:new frontend-k8s-deployment`
2. **Fast-forward**: `/opsx:ff frontend-k8s-deployment` (generate all artifacts)
3. **Keep exploring**: Dig into specific aspects (Dockerfile, Caddyfile, HTTPRoute, etc.)

---

## Sources

- [Caddy vs Nginx vs Apache comparison](https://blog.logrocket.com/comparing-best-web-servers-caddy-apache-nginx/)
- [2026 web server guide](https://www.vpsmalaysia.com.my/blog/apache-vs-nginx-vs-litespeed-vs-caddy/)
- [Caddy features](https://caddyserver.com/features)
- [Top CDN providers 2026](https://www.inmotionhosting.com/blog/top-cdn-providers/)
- [Cloudflare vs CloudFront comparison](https://www.cloudoptimo.com/blog/cloudfront-vs-cloudflare-vs-akamai-choosing-the-right-cdn-in-2025/)
