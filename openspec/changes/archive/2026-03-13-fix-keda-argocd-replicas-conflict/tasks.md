## 1. Fix Deployment Manifest

- [x] 1.1 Remove `replicas: 1` from `k8s/namespaces/backend/base/consumer/deployment.yaml`
- [x] 1.2 Run `make lint-k8s` to validate the manifest renders correctly without replicas

## 2. Add ignoreDifferences to ArgoCD Application

- [x] 2.1 Add `ignoreDifferences` for `spec.replicas` on `consumer-app` Deployment to the `backend` ArgoCD Application definition
- [x] 2.2 Run `make lint` to validate all changes

## 3. Deploy and Verify

- [x] 3.1 Create PR to cloud-provisioning
- [x] 3.2 Merge PR and verify ArgoCD syncs to Synced/Healthy
- [x] 3.3 Confirm the OutOfSync loop has stopped (generation count stable, no selfHeal attempts)
