## Why

The `liverty-music-prod` GCP project is currently empty — the Pulumi code short-circuits with `if (environment === 'prod') return;` in both `kubernetes.ts` and `network.ts`. This was a deliberate cost-saving measure while the product had no users. We now need to provision prod to prepare for the upcoming user-facing launch, and several foundational decisions are irreversible (Dataplane V2 enable, etcd CMEK enable, regional vs zonal, network CIDR layout). Those decisions must be made and recorded now so the prod cluster does not need to be rebuilt later when audit or scale demands them.

## What Changes

- Provision a new GKE Standard regional cluster in `asia-northeast2` for prod, replacing the current `return` short-circuit in `kubernetes.ts`.
- **Enable Dataplane V2** (`datapathProvider: 'ADVANCED_DATAPATH'`) on the prod cluster. Irreversible after creation. Aligns with GCP's announced 2027-03-30 default change.
- **Enable Application-layer Secrets Encryption** (etcd CMEK) using a new Cloud KMS key in the prod project. Irreversible at cluster creation. Prepares for SOC2 / blockchain security audit gates.
- Provision the prod-side VPC, subnet, and secondary IP ranges using the same CIDR plan as dev (`10.10.0.0/20` nodes, `10.20.0.0/16` pods, `10.30.0.0/20` services, `172.16.0.0/28` master). No conflict because environments are GCP-project-separated.
- Provision a single Spot `e2-medium` node pool mirroring dev's config (30 GB pd-standard boot disk, autoscale 1-3 nodes, Shielded Nodes enabled). Cost-first phase.
- Leave `enablePrivateNodes: false` initially and skip Cloud NAT in the prod VPC. Both are mutable and will be enabled once real users arrive.
- Skip Google Managed Prometheus, restrict logging to `SYSTEM_COMPONENTS` + `WORKLOADS` (same as dev's current state).
- Skip cluster-level Confidential GKE Nodes (irreversible if enabled; deferred to blockchain mainnet phase as a dedicated node pool).
- Skip boot disk CMEK and HSM-protected keys (deferred to compliance gates).
- Provision peripheral GCP resources to bring prod to parity with dev: prod Cloud SQL Postgres instance (PSC-only, IAM auth), prod Artifact Registry repos (backend, frontend), prod GCP Service Accounts (gke-node, backend-app, otel-collector, zitadel, eso, image-updater), prod Secret Manager entries for the same keys dev has, prod Cloud DNS public zone for the prod domain, prod Certificate Manager + Gateway static IP, prod ArgoCD bootstrap.
- **BREAKING**: First `pulumi up` for the prod stack after this change is merged will create real GCP infrastructure and incur ongoing cost. The Pulumi deployment flow remains manual-trigger for prod per existing `deployment-infrastructure` spec.

## Capabilities

### New Capabilities

- `prod-environment-bootstrap`: Irreversible prod-specific infrastructure decisions (regional GKE Standard cluster, Dataplane V2 enable, etcd CMEK key, IP CIDR plan, Spot/public-node cost-first defaults) plus the contract that prod runs the same workload set as dev. This capability captures the choices that cannot be safely undone, so future changes can rely on them.

### Modified Capabilities

- (none) — existing `gke-standard-infrastructure`, `deployment-infrastructure`, `gcp-cost-guardrails`, and similar specs already describe dev-only or env-aware behavior. None of their requirements are changing — the prod cluster's behavior is additive and recorded in the new `prod-environment-bootstrap` capability.

## Impact

- **Pulumi code changes** (in `cloud-provisioning/src/gcp/`):
  - `components/kubernetes.ts`: replace `if (environment === 'prod') return;` block with a prod Standard regional cluster definition (cluster + node pool + KMS key + databaseEncryption).
  - `components/network.ts`: remove `if (environment === 'prod') return;` short-circuit. Provision prod public DNS zone, Certificate Manager (DnsAuth + Certificates + CertificateMap), per-service certs, static IP, and DNS records. Skip Cloud NAT for prod in this phase.
  - `components/postgres.ts`: provision prod Cloud SQL instance with same shape as dev.
  - `index.ts`: nothing changes — `NetworkConfig.Osaka` constants are already env-agnostic and re-used.
- **Kubernetes manifests** (in `cloud-provisioning/k8s/`):
  - Existing prod overlays already exist for some apps (need to audit and align with dev's current state).
  - Some namespaces (e.g., `zitadel`) currently only have dev overlays — add prod overlays.
- **Cloud KMS** (new for prod project):
  - KeyRing `gke-cluster` in `asia-northeast2`.
  - CryptoKey `gke-etcd-encryption` (PURPOSE_ENCRYPT_DECRYPT, software-backed).
  - IAM: GKE service agent granted `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key.
- **Cost impact** (rough estimate, first month):
  - Regional cluster management fee: ~$72/month (= $0.10/hr × 720 hr, regional Standard does not qualify for free tier).
  - Compute Engine (Spot e2-medium × 2-3 nodes): ~$30-60/month estimated.
  - Cloud SQL (db-f1-micro or similar): ~$10-20/month.
  - Cloud KMS software key + ops: ~$0.20/month.
  - **Total estimated initial monthly cost**: ¥15,000-25,000.
- **DNS / TLS**: prod domain (currently `liverty-music.app` apex per `Postmark` integration) needs Cloudflare delegation flipped from dev-only behavior. Existing dev pattern (Cloud DNS subzone with NS delegation from Cloudflare) needs prod-specific configuration since prod uses the apex domain, not a subdomain.
- **Reference documentation**: `cloud-provisioning/docs/PROD_BOOTSTRAP_DECISIONS.md` and `cloud-provisioning/docs/GKE_CLUSTER_MODE_DECISION.md` already document the underlying reasoning and irreversible-vs-reversible reference tables. They are the operational source-of-truth that this OpenSpec change formalizes into testable requirements.
- **Future revisit triggers** (out of scope for this change, documented for traceability):
  - First real users → enable private nodes, Cloud NAT, GMP, add non-Spot node pool.
  - Blockchain mainnet → KMS-based signing keys, dedicated Confidential node pool, infra security audit.
  - SOC2 Type II → boot disk CMEK, key rotation policy, audit trail completeness review.
