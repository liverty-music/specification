## Why

Dev environment deployments currently require manual intervention to update image tags in the cloud-provisioning repository after each backend merge. With multiple merges per day, this creates friction. We need automated deployment for dev while maintaining manual control for production, without polluting commit history with automated image update commits.

## What Changes

- Install and configure ArgoCD Image Updater with `argocd` write-back method (no Git commits)
- Configure automated image updates for dev environment via ArgoCD Application parameter overrides
- Maintain manual GitHub Release workflow for production deployments
- Set up proper imagePullPolicy and 30-second polling interval

## Capabilities

### New Capabilities
- `argocd-image-automation`: Automated container image updates for dev environment using ArgoCD Image Updater with in-cluster parameter overrides (zero commit spam)

### Modified Capabilities
<!-- No existing capabilities are being modified -->

## Impact

- **cloud-provisioning repo**: New ArgoCD Application annotations for Image Updater, Image Updater Kustomize manifests in argocd namespace
- **backend repo**: Deployment manifests need imagePullPolicy adjustments
- **ArgoCD cluster**: Image Updater installation, RBAC configuration, 30s polling interval
- **No Git write-back**: Image updates are applied as ArgoCD Application parameter overrides, not Git commits
