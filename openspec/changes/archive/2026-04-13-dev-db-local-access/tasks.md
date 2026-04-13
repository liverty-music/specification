## 1. K8s Manifest — Cloud SQL Auth Proxy Deployment (dev overlay)

- [x] 1.1 Create `k8s/namespaces/backend/overlays/dev/sql-proxy/deployment.yaml` with Cloud SQL Auth Proxy v2, `--psc`, `--auto-iam-authn`, `--port=5432`, and `backend-app` ServiceAccount
- [x] 1.2 Add `sql-proxy/deployment.yaml` to `k8s/namespaces/backend/overlays/dev/kustomization.yaml` resources

## 2. Documentation — backend/AGENTS.md

- [x] 2.1 Add a "Dev DB Access" section to `backend/AGENTS.md` with the `kubectl port-forward` command, `psql` connection string, and a note that it is dev-only (not for local Docker Compose)

## 3. Skill Update — go-postgres

- [x] 3.1 Add a "Dev DB Access" section to `~/.claude/skills/go-postgres/SKILL.md` with the port-forward procedure and connection parameters for the dev Cloud SQL instance

## 4. Verification

- [x] 4.1 Confirm `kubectl port-forward deployment/cloud-sql-proxy 5432:5432 -n backend` connects successfully after ArgoCD sync
- [x] 4.2 Confirm `psql "host=localhost port=5432 user=backend-app@liverty-music-dev.iam dbname=liverty-music sslmode=disable options='-c search_path=app'"` returns a prompt
