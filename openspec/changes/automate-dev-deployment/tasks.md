## 1. ArgoCD Image Updater Installation

- [ ] 1.1 Create Kustomize base for Image Updater in k8s/namespaces/argocd/base/ (deployment, service account, RBAC)
- [ ] 1.2 Configure Image Updater with --interval 30s flag
- [ ] 1.3 Create dev overlay for Image Updater in k8s/namespaces/argocd/overlays/dev/
- [ ] 1.4 Add Image Updater resources to argocd namespace kustomization
- [ ] 1.5 Verify Image Updater manifests render correctly with kubectl kustomize

## 2. Backend ArgoCD Application Annotations

- [ ] 2.1 Add Image Updater annotations to dev backend ArgoCD Application (image-list, update-strategy)
- [ ] 2.2 Verify annotation specifies correct GAR path for backend server image
- [ ] 2.3 Verify write-back-method defaults to "argocd" (no explicit annotation needed)
- [ ] 2.4 Verify dev backend Application renders correctly with kubectl kustomize

## 3. Frontend ArgoCD Application Annotations

- [ ] 3.1 Add Image Updater annotations to dev frontend ArgoCD Application (image-list, update-strategy)
- [ ] 3.2 Verify annotation specifies correct GAR path for frontend web-app image
- [ ] 3.3 Verify dev frontend Application renders correctly with kubectl kustomize

## 4. Backend Deployment imagePullPolicy

- [ ] 4.1 Set imagePullPolicy: Always on backend server deployment in base
- [ ] 4.2 Set imagePullPolicy: Always on concert-discovery CronJob in base
- [ ] 4.3 Verify deployment manifests render correctly with kubectl kustomize

## 5. Frontend Deployment imagePullPolicy

- [ ] 5.1 Set imagePullPolicy: Always on frontend web-app deployment in base
- [ ] 5.2 Verify deployment manifests render correctly with kubectl kustomize

## 6. Production Environment Verification

- [ ] 6.1 Verify prod backend ArgoCD Application has NO Image Updater annotations
- [ ] 6.2 Verify prod frontend ArgoCD Application has NO Image Updater annotations (if prod apps exist)

## 7. End-to-End Testing

- [ ] 7.1 Deploy changes to dev cluster (pulumi up or ArgoCD sync)
- [ ] 7.2 Verify Image Updater pod is running and healthy in argocd namespace
- [ ] 7.3 Check Image Updater logs for successful registry scan
- [ ] 7.4 Trigger a backend image build by merging a PR to main
- [ ] 7.5 Verify Image Updater detects new digest within ~30 seconds
- [ ] 7.6 Verify ArgoCD Application shows updated kustomize image override
- [ ] 7.7 Verify new backend pod is running with updated image digest
- [ ] 7.8 Verify no commits were created in cloud-provisioning repo

## 8. Rollback Testing

- [ ] 8.1 Use ArgoCD UI to rollback dev application to previous sync
- [ ] 8.2 Verify rollback deploys previous image
- [ ] 8.3 Verify Image Updater re-applies latest digest on next polling cycle
