## 1. Update ArgoCD Application Annotations

- [x] 1.1 Add `concert-discovery` to `image-list` annotation in `k8s/argocd-apps/dev/backend.yaml`
- [x] 1.2 Add `concert-discovery.update-strategy: digest` annotation
- [x] 1.3 Add `concert-discovery.allow-tags: regexp:^main$` annotation
- [x] 1.4 Add `server.kustomize.image-name: server` annotation
- [x] 1.5 Add `consumer.kustomize.image-name: consumer` annotation
- [x] 1.6 Add `concert-discovery.kustomize.image-name: concert-discovery` annotation

## 2. Validate

- [x] 2.1 Run `kubectl kustomize k8s/namespaces/backend/overlays/dev` to verify Kustomize renders without errors
- [x] 2.2 Verify the ArgoCD Application YAML is valid (no syntax errors in annotations)
