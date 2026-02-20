## 1. GCP Secret Manager Resources (Pulumi)

- [x] 1.1 Add Secret Manager resources inline in `KubernetesComponent` (`src/gcp/components/kubernetes.ts`) with secret + version + IAM binding
- [x] 1.2 Add `secretmanager.googleapis.com` to enabled APIs in `api.ts`
- [x] 1.3 Provision `lastfm-api-key` secret with version (value from Pulumi ESC config key `gcp.lastFmApiKey`)
- [x] 1.4 Grant `roles/secretmanager.secretAccessor` to `backend-app` service account on the secret

## 2. External Secrets Operator Deployment (ArgoCD)

- [x] 2.1 Create ArgoCD Application manifest for ESO Helm chart (`k8s/namespaces/external-secrets/`) targeting `external-secrets` namespace
- [x] 2.2 Configure ESO Helm values (replicas, resource requests for Autopilot, service account for Workload Identity)

## 3. Kubernetes Secret Sync Manifests (Kustomize)

- [x] 3.1 Create `ClusterSecretStore` resource referencing GCP Secret Manager with Workload Identity auth in `k8s/namespaces/external-secrets/base/`
- [x] 3.2 Create `ExternalSecret` resource mapping `lastfm-api-key` → `LASTFM_API_KEY` key in `backend-secrets` K8s Secret
- [x] 3.3 Add environment-specific `ClusterSecretStore` patches in `k8s/namespaces/external-secrets/overlays/dev/`
- [x] 3.4 Add Kustomize resources entries for new manifests in `kustomization.yaml`

## 4. Backend Deployment Update

- [x] 4.1 Add `envFrom: secretRef: backend-secrets` to backend Deployment alongside existing ConfigMap
- [x] 4.2 Remove `LASTFM_API_KEY` from ConfigMap if present (was never present — nothing to do)
- [x] 4.3 Add Reloader annotation `reloader.stakater.com/auto: "true"` to Deployment metadata

## 5. Reloader Deployment (ArgoCD)

- [x] 5.1 Create ArgoCD Application manifest for Stakater Reloader Helm chart
- [x] 5.2 Configure Reloader Helm values (resource requests for Autopilot, namespace scope)

## 6. Verification

- [x] 6.1 Run `pulumi preview` to verify GCP Secret Manager resources
- [x] 6.2 Verify ESO controller is running and ClusterSecretStore reports Ready
- [x] 6.3 Verify ExternalSecret syncs and `backend-secrets` K8s Secret is created with correct keys
- [x] 6.4 Verify backend pod starts successfully and reads `LASTFM_API_KEY` from the Secret
