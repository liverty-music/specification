## Why

Dev environment deployments currently require manual intervention to update image tags in the cloud-provisioning repository after each backend merge. With multiple merges per day, this creates friction and pollutes commit history with repetitive "update image tag" commits. We need automated deployment for dev while maintaining manual control for production.

## What Changes

- Install and configure ArgoCD Image Updater to watch Google Artifact Registry (GAR)
- Configure automated image tag updates for dev environment only
- Maintain manual GitHub Release workflow for production deployments
- Set up proper imagePullPolicy and image update strategies

## Capabilities

### New Capabilities
- `argocd-image-automation`: Automated container image updates for dev environment using ArgoCD Image Updater

### Modified Capabilities
<!-- No existing capabilities are being modified -->

## Impact

- **cloud-provisioning repo**: New ArgoCD Application annotations, Image Updater configuration
- **backend repo**: Deployment manifests need imagePullPolicy adjustments
- **ArgoCD cluster**: Image Updater installation and RBAC configuration
- **Git write-back**: Automated commits to cloud-provisioning repo for dev image updates
