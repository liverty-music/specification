## Why

Runtime secrets (starting with `LASTFM_API_KEY`) are currently unmanaged -- there is no secure mechanism to provision, store, or rotate API keys for Kubernetes workloads. The backend config (`config.go`) reads these values from environment variables, but no K8s Secret or secret store backs them. As the platform grows, more external API keys and credentials will be needed, making a centralized secret management solution essential now.

## What Changes

- Provision GCP Secret Manager resources via Pulumi (secret creation, IAM bindings for `backend-app` service account)
- Deploy External Secrets Operator (ESO) into the GKE Autopilot cluster
- Define `SecretStore` and `ExternalSecret` Kustomize manifests to sync GCP secrets into K8s Secrets
- Update the backend Deployment to consume secrets via `envFrom: secretRef` alongside the existing ConfigMap
- Establish a pattern for adding future secrets without application code changes

## Capabilities

### New Capabilities
- `secret-management`: Secure provisioning, storage, and synchronization of runtime secrets from GCP Secret Manager to Kubernetes pods via External Secrets Operator

### Modified Capabilities
- `deployment-infrastructure`: Backend Deployment gains a `secretRef` in `envFrom` to load secrets from a K8s Secret managed by ESO

## Impact

- **Infrastructure (Pulumi)**: New GCP Secret Manager resources, IAM role bindings (`roles/secretmanager.secretAccessor`), ESO Helm release or ArgoCD Application
- **Kubernetes manifests**: New CRDs (`SecretStore`, `ExternalSecret`) in `k8s/namespaces/backend/`, Deployment patch for `secretRef`
- **Backend application**: No code changes -- `os.Getenv("LASTFM_API_KEY")` continues to work as-is
- **ArgoCD**: ESO system components need to be managed (Helm chart or dedicated Application)
- **Security**: Secrets stored in GCP Secret Manager (encrypted at rest), synced to K8s Secrets (GKE etcd encryption), accessed via Workload Identity (no static credentials)
