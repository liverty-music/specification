## 1. ArgoCD component cleanup

- [x] 1.1 Disable dex-server in `k8s/namespaces/argocd/base/values.yaml` (`dex.enabled: false`)
- [x] 1.2 Disable notifications-controller in `k8s/namespaces/argocd/base/values.yaml` (`notifications.enabled: false`)
- [x] 1.3 Remove dex and notifications resource blocks from `values.yaml` (requests/limits no longer needed)

## 2. ArgoCD resource right-sizing

- [x] 2.1 Update `k8s/namespaces/argocd/base/values.yaml` resource requests/limits for remaining components: controller (50m/128Mi), repoServer (50m/64Mi), server (50m/64Mi), redis (50m/52Mi), redisSecretInit (50m/52Mi), applicationSet (50m/64Mi)
- [x] 2.2 Verify rendered manifests with `kubectl kustomize --enable-helm k8s/namespaces/argocd/overlays/dev`

## 3. Backend optimization

- [x] 3.1 Add replicas patch to `k8s/namespaces/backend/overlays/dev/kustomization.yaml` to set server-app replicas to 1
- [x] 3.2 Add resource request/limit patch for server-app in dev overlay (50m CPU / 64Mi memory request)
- [x] 3.3 Add Spot VM nodeSelector patch targeting `kind: CronJob` in `k8s/namespaces/backend/overlays/dev/kustomization.yaml`
- [x] 3.4 Verify rendered manifests with `kubectl kustomize k8s/namespaces/backend/overlays/dev`

## 4. External Secrets resource right-sizing

- [x] 4.1 Update `k8s/namespaces/external-secrets/base/values.yaml` resource requests/limits: controller (50m/64Mi), webhook (50m/52Mi), certController (50m/52Mi)
- [x] 4.2 Verify rendered manifests with `kubectl kustomize --enable-helm k8s/namespaces/external-secrets/overlays/dev`

## 5. Frontend resource right-sizing

- [x] 5.1 Add resource request/limit patch for web-app in `k8s/namespaces/frontend/overlays/dev` (50m CPU / 52Mi memory request)
- [x] 5.2 Verify rendered manifests with `kubectl kustomize k8s/namespaces/frontend/overlays/dev`

## 6. Reloader resource right-sizing

- [x] 6.1 Update `k8s/namespaces/reloader/base/values.yaml` resource requests/limits (50m CPU / 64Mi memory request)
- [x] 6.2 Verify rendered manifests with `kubectl kustomize --enable-helm k8s/namespaces/reloader/overlays/dev`

## 7. Final validation

- [x] 7.1 Run kustomize dry-run for all dev overlays and confirm no errors
- [x] 7.2 Verify all workloads have Spot VM nodeSelector in rendered output
