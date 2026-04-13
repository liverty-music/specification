## Context

Cloud SQL is configured with PSC (Private Service Connect) only — no public IP. The PSC endpoint (`10.10.10.10`) is reachable only from within the GKE cluster's VPC (`global-vpc`). Local machines have no VPN or direct VPC route.

The backend application uses the Cloud SQL Go Connector SDK with `WithPSC()` + `WithIAMAuthN()` options directly in-process. This works for production workloads running in GKE, but does not help developers or Claude Code agents who need direct DB access from outside the cluster.

The dev environment already has:
- `backend-app` Kubernetes ServiceAccount with Workload Identity binding to `backend-app@liverty-music-dev.iam.gserviceaccount.com`
- That GSA has `roles/cloudsql.instanceUser` on the dev Cloud SQL instance
- Private DNS zone `asia-northeast2.sql.goog.` resolves from within the cluster

## Goals / Non-Goals

**Goals:**
- Enable `psql`, DBeaver, Atlas CLI, and other local tools to connect to the dev Cloud SQL instance
- Enable Claude Code agents to run queries against the dev DB by following documented steps
- No new GCP IAM roles, service accounts, or VPN infrastructure required
- Dev-only: staging/prod remain unchanged

**Non-Goals:**
- Persistent always-on tunnel (port-forward is ephemeral by design)
- Access to staging or production DB
- Replacing local Docker Compose for integration tests (that workflow stays as-is)
- GUI tooling setup (DBeaver configuration is user responsibility)

## Decisions

### Decision 1: Cloud SQL Auth Proxy as a standalone K8s Deployment (not sidecar)

**Chosen**: Standalone `Deployment` in a new `tools` namespace with `kubectl port-forward` for access.

**Alternatives considered**:
| Option | Pros | Cons |
|--------|------|------|
| IAP SSH tunnel to GKE node | No new K8s resources | Requires SSH access to nodes, complex setup, must install Auth Proxy on node |
| Cloud VPN | Transparent access, no port-forward | Expensive setup, requires new Pulumi infra, overkill for dev access |
| Cloud Shell | Zero setup | Not suitable for scripted/agent use, session-based |
| Standalone Proxy Deployment (chosen) | Simple, uses existing WI, kubectl only, dev-only cost | port-forward session can drop |

A standalone Deployment (not sidecar) is preferred so it can be shared across developers without modifying backend app manifests.

### Decision 2: Reuse `backend-app` ServiceAccount

The existing `backend-app` KSA already has Workload Identity bound to the GSA with `cloudsql.instanceUser`. Creating a separate SA would require new Pulumi code and a new GSA IAM binding.

**Constraint**: The Auth Proxy Pod must be in the `backend` namespace to use the `backend-app` KSA, OR a new KSA with the same WI annotation must be created in `tools`. We choose the `backend` namespace to avoid creating new IAM bindings.

### Decision 3: Auth Proxy image and flags

- Image: `gcr.io/cloud-sql-connectors/cloud-sql-proxy:2` (latest v2.x)
- Flags: `--psc`, `--auto-iam-authn`, `--port=5432`
- Instance connection name: `liverty-music-dev:asia-northeast2:postgres-osaka`
- DNS resolves within cluster via existing private zone `asia-northeast2.sql.goog.`

### Decision 4: Document in AGENTS.md and go-postgres skill

Claude Code agents receive `backend/AGENTS.md` in context automatically. Adding the port-forward procedure there ensures agents know the correct connection string and steps without requiring the user to explain it each time.

The `go-postgres` skill is consulted when writing DB code — adding a "Dev DB Access" section there provides the connection info at the right moment.

## Risks / Trade-offs

- **`kubectl port-forward` drops on inactivity** → Mitigation: Document that the user must keep the terminal open; provide the exact reconnect command
- **Proxy Pod always running in dev costs CPU/memory** → Mitigation: Use minimal resources (10m CPU, 32Mi memory); deploy dev-only via overlay
- **Auth Proxy v2 requires correct DNS resolution** → Mitigation: Cluster already has the required private DNS zone; no additional DNS setup needed
- **IAM token expiry** → The Auth Proxy automatically refreshes IAM tokens; no manual action needed

## Migration Plan

1. Add `k8s/namespaces/backend/overlays/dev/sql-proxy/` manifest (Deployment + no new SA)
2. Add to dev overlay `kustomization.yaml`
3. Update `backend/AGENTS.md` with connection procedure
4. Update `~/.claude/skills/go-postgres/SKILL.md` with Dev DB Access section
5. ArgoCD auto-syncs the new Deployment on PR merge — no manual rollout needed

Rollback: remove the overlay resource and re-sync ArgoCD. No state is stored in the proxy pod.

## Open Questions

- Should the proxy Deployment have `replicas: 0` by default and scale to 1 only when needed (to save resources)? → Current decision: `replicas: 1` always-on in dev for simplicity; revisit if dev cluster cost becomes a concern.
