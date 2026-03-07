## Context

The ArgoCD backend Application (`k8s/argocd-apps/dev/backend.yaml`) uses `argocd-image-updater` with `write-back-method: argocd` to track container images via digest strategy. The Kustomize bases for server, consumer, and concert-discovery all use short alias names in `images[].name` (e.g., `consumer`) mapped to full registry paths via `newName`.

When image-updater writes back to `spec.source.kustomize.images`, it uses the full registry path as the override key. This doesn't match the short Kustomize `name`, so the override is silently ignored for images that were never bootstrapped. Server works by accident (likely bootstrapped during initial setup), but consumer and concert-discovery were never written.

## Goals / Non-Goals

**Goals:**
- All three backend images (server, consumer, concert-discovery) are automatically rolled out when new `main`-tagged images are pushed
- Explicit `kustomize.image-name` mapping for all images to prevent future regression

**Non-Goals:**
- Changing the write-back method (argocd → git) — current method is fine
- Modifying Kustomize base structure or image naming conventions
- Adding image tracking for other environments (staging/prod)

## Decisions

### Use `kustomize.image-name` annotation (not change Kustomize names)

**Choice**: Add `<alias>.kustomize.image-name` annotations to map image-updater aliases to Kustomize short names.

**Alternative considered**: Change `images[].name` in Kustomize bases to use full registry paths and update `deployment.yaml` image references. Rejected because it would require changes across multiple files, break the clean separation of image name from registry path, and potentially disrupt existing deployments.

**Alternative considered**: Manually bootstrap the consumer/concert-discovery entries in the live Application object. Rejected because it's fragile — any full sync or Application recreation would lose the entries.

### Add concert-discovery to image-list

**Choice**: Include `concert-discovery` in the `image-list` annotation with the same digest strategy and `main` tag filter as the other images.

**Rationale**: The deploy workflow already pushes `concert-discovery` with the `main` tag. Without image-updater tracking, the CronJob continues running stale images after backend merges.

### Add kustomize.image-name for server too

**Choice**: Add `server.kustomize.image-name: server` even though server currently works.

**Rationale**: Server works by coincidence (bootstrapped entry). Making the mapping explicit prevents regression if the Application is recreated or the entry is lost during a sync.

## Risks / Trade-offs

- **[Risk] concert-discovery CronJob may have different update cadence needs** → Mitigation: Using the same `main` tag filter as server/consumer. If a different strategy is needed later, the annotation can be updated independently.
- **[Risk] image-updater processes more images per check interval** → Mitigation: Adding one more image (concert-discovery) has negligible performance impact on image-updater polling.
