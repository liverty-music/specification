# GCP Cost Analysis — liverty-music-dev (March 2026)

## Billing Summary (Mar 2 – Mar 31)

| Service | Usage Cost | Savings | Subtotal | % Change |
|---------|-----------|---------|----------|----------|
| Kubernetes Engine | ¥14,055 | -¥5,447 | ¥8,608 | +6% |
| Networking | ¥7,352 | -¥2,463 | ¥4,889 | +41% |
| Cloud Monitoring | ¥4,721 | ¥0 | ¥4,721 | +33% |
| Vertex AI | ¥2,627 | ¥0 | ¥2,627 | +1312% |
| Cloud SQL | ¥1,841 | ¥0 | ¥1,841 | +2% |
| Compute Engine | ¥669 | ¥0 | ¥669 | +346% |
| Cloud DNS | ¥61 | ¥0 | ¥61 | +15% |
| Artifact Registry | ¥35 | ¥0 | ¥35 | — |

Savings program: Spending-based discount

---

## Infrastructure Configuration (as-is)

### GKE Cluster

- **Name**: `cluster-osaka`
- **Mode**: Autopilot
- **Location**: `asia-northeast2` (Osaka), zonal (`asia-northeast2-a`)
- **Kubernetes version**: v1.34.4-gke.1193000
- **Active nodes**: 2 (as of investigation date)
  - `gk3-cluster-osaka-nap-*` (Node Auto Provisioning, 10h old)
  - `gk3-cluster-osaka-pool-6-*` (2d11h old)
- **Spot scheduling**: `cloud.google.com/compute-class: autopilot-spot` (all dev workloads)
- **Private nodes**: `enablePrivateNodes: true`
- **Private endpoint**: `enablePrivateEndpoint: false` (control plane is public)
- **masterAuthorizedNetworks**: not configured (control plane accessible from any IP)
- **Dataplane**: Advanced Datapath (Dataplane V2)

### Deployed Workloads (~20 pods across 10 namespaces)

| Namespace | Workloads |
|-----------|-----------|
| backend | server-app (1 replica), consumer-app (KEDA 0–2) |
| frontend | web-app (1 replica) |
| argocd | 7 pods (controller, server, redis, repo-server, etc.) |
| atlas-operator | 1 pod |
| external-secrets | 3 pods |
| keda | 3 pods |
| nats | nats-0 (StatefulSet) |
| otel-collector | 1 pod (2 restarts observed) |
| reloader | 1 pod |
| gateway | GKE L7 Gateway (managed) |

### Cloud SQL

- **Instance**: `postgres-osaka`
- **Version**: PostgreSQL 18
- **Tier**: `db-f1-micro`
- **Availability**: ZONAL (dev)
- **Connectivity**: Private Service Connect (PSC), internal IP 10.10.10.10
- **SSL**: ENCRYPTED_ONLY

### Networking

- **VPC**: `vpc-osaka`, custom, `asia-northeast2`
- **Subnet**: `cluster-subnet-osaka`, 10.10.0.0/20
- **Pod CIDR**: 10.20.0.0/16
- **Services CIDR**: 10.30.0.0/20
- **Cloud NAT**: `nat-osaka`, AUTO_ONLY IPs, ALL_SUBNETWORKS_ALL_IP_RANGES, dynamic port allocation enabled
- **Cloud Router**: `nat-router-osaka`
- **L7 LB**: GKE Gateway (`gke-l7-global-external-managed`), static IP `api-gateway-static-ip`, HTTPS :443
- **Forwarding rules**: 1 (HTTPS listener)
- **HTTPRoutes**: backend (`api.dev.liverty-music.app`), frontend (`dev.liverty-music.app`)
- **Cross-zone traffic**: none (single-zone cluster)
- **`privateIpGoogleAccess`**: `true` on subnet (already set in Pulumi)
- **PGA DNS zones**: NOT configured (`restricted.googleapis.com` / `googleapis.com` private zones missing)

### Vertex AI / Gemini

- **Model**: `gemini-3-flash-preview` (all environments)
- **Location**: `global` (config), `asia-northeast2` (code)
- **Used by**: `concert-discovery` CronJob
- **Dev schedule**: Fridays only (`0 9 * * 5`) → ~4 runs/month
- **Prod/staging schedule**: Daily (`0 9 * * *`)
- **Processing**: All `followed_artists` per run (no batch limit)
  - Dev: 3,157 artists (as of 2026-04-01)
- **Google Search grounding**: enabled
- **MaxOutputTokens**: 16,384
- **searchCacheTTL**: 24h (skips artist if searched within 24h)

---

## Cost Root Cause Analysis

### GKE ¥14,055

- **Primary**: Autopilot cluster management fee $0.10/hr × 720h = **$72/月 = ¥10,800** (fixed, unavoidable on Autopilot)
- **Secondary**: Pod-request-based compute (Spot discount already applied → subtotal ¥8,608)

### Networking ¥7,352

- **Cloud NAT gateway fee**: $0.045/hr × 720h = $32.4 = **¥4,860** (fixed)
- **Cloud NAT external IP**: ~¥432 (fixed)
- **L7 Global LB forwarding rule**: $0.025/hr × 720h = $18 = **¥2,700** (fixed)
- **Static IP**: ~¥216 (fixed)
- **NAT data processing**: $0.045/GiB — includes Google API traffic that bypasses PGA due to missing DNS zones
- Total fixed: ~¥8,200 before spending-based discount

### Vertex AI ¥2,627 (+1312%)

- `gemini-3-flash-preview` billing started **2026-01-05**; prior month had no charge → explains spike
- Grounding pricing for Gemini 3 preview: **$14/1,000 search queries** (not per prompt), free tier **5,000 queries/month**
- Dev: ~12,628 queries/month (3,157 artists × 4 runs) → ~7,628 billable → $106 theoretical
- Actual ¥2,627 ≈ token cost only → suggests grounding queries still within free tier or counted differently
- **Scale risk**: at 10,000 artists, grounding cost reaches ~¥1.3M/month if uncapped

### Cloud Monitoring ¥4,721

- GMP (Managed Prometheus) is mandatory on Autopilot v1.25+, cannot be disabled
- **Free**: GKE system metrics, Google Cloud platform metrics
- **Billed**: Custom application metrics (KEDA NATS metrics, OTel spans)
- Cloud Trace: $0.20/M spans (2.5M free/month)
- Primary cost likely Cloud Logging ingestion (50 GiB/month free, $0.50/GiB after)

---

## Official Pricing Reference (JPY @ ¥150/USD)

| SKU | Price |
|-----|-------|
| GKE Autopilot cluster management | $0.10/hr = ¥10,800/月 |
| GKE Standard zonal (1st cluster) | **¥0** |
| GKE Autopilot vCPU (us-central1) | $0.0445/hr |
| GKE Autopilot memory | $0.0049/GiB/hr |
| e2-standard-2 Spot | ~$0.027/hr |
| Cloud NAT gateway | $0.045/hr = ¥4,860/月 |
| Cloud NAT data processing | $0.045/GiB |
| L7 Global LB forwarding rule | $0.025/hr = ¥2,700/月 |
| Gemini 3 preview grounding | $14/1,000 search queries (5,000/月 free) |
| Gemini 2.0 Flash grounding | $35/1,000 grounded prompts (1,500/日 free) |
| Cloud Monitoring metrics (samples) | $0.06/M samples |
| Cloud Logging storage | $0.50/GiB (50 GiB/月 free) |
| Cloud Trace | $0.20/M spans (2.5M/月 free) |
| Internet egress (Premium, asia) | $0.12/GiB (first 1 TB) |

---

## Proposed Changes

| Change | Location | Estimated Savings |
|--------|----------|-------------------|
| [`gke-cost-optimization`](../changes/gke-cost-optimization/) | Autopilot→Standard + public nodes + NAT removal | ~¥16,000/月 |
| [`private-google-access`](../changes/private-google-access/) | PGA DNS zones for googleapis.com | NAT data processing 削減 (staging/prod) |

### `gke-cost-optimization` 削減内訳

| 項目 | 削減額 |
|------|--------|
| GKE management fee 消滅 | -¥10,800/月 |
| Cloud NAT gateway + IP 固定費 | -¥5,292/月 |
| **合計** | **~¥16,000/月** |

### `private-google-access` 削減内訳

- NAT data processing から Google API トラフィック分を除外
- staging/prod の private cluster で有効
- 削減額は実際の Google API egress 量次第（Cloud NAT metrics で確認要）
