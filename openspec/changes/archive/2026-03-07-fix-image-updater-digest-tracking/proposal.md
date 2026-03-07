## Why

The argocd-image-updater is configured to track `server`, `consumer`, and `concert-discovery` images via digest strategy, but only `server` gets its digest written to the ArgoCD Application's `spec.source.kustomize.images`. The consumer and concert-discovery deployments are never rolled out when new images are pushed. This is because the image-updater uses the full registry path as the kustomize override key, which doesn't match the short alias (`consumer`, `concert-discovery`) defined in each Kustomize base's `images[].name`.

## What Changes

- Add `kustomize.image-name` annotations for `server`, `consumer`, and `concert-discovery` to the ArgoCD backend Application, mapping each image alias to its short Kustomize name.
- Add `concert-discovery` to the `image-list` annotation with digest strategy and `main` tag filter, so it is also tracked by argocd-image-updater.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none - this is an infrastructure/configuration fix, no spec-level behavior changes)

## Impact

- **ArgoCD Application**: `k8s/argocd-apps/dev/backend.yaml` (annotation changes only)
- **Affected deployments**: `consumer-app` Deployment and `concert-discovery-app` CronJob will now be automatically rolled out on new image pushes, matching the existing `server-app` behavior.
- **No breaking changes**: The server image tracking continues to work as before; annotations are additive.
