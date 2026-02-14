## 1. ArgoCD Image Updater Installation

- [ ] 1.1 Install ArgoCD Image Updater manifest to argocd namespace
- [ ] 1.2 Verify Image Updater pod is running and healthy
- [ ] 1.3 Check Image Updater logs for startup errors
- [ ] 1.4 Verify Image Updater can access ArgoCD API server

## 2. Git Write-Back Configuration

- [ ] 2.1 Verify ArgoCD repo secret exists and has write permissions
- [ ] 2.2 Test Image Updater can read ArgoCD repo credentials
- [ ] 2.3 Configure Image Updater to use git write-back method
- [ ] 2.4 Set commit author name and email for automated commits

## 3. Backend Deployment Manifest Updates

- [ ] 3.1 Update backend deployment.yaml to set imagePullPolicy: Always
- [ ] 3.2 Verify deployment manifest uses correct image name placeholder
- [ ] 3.3 Commit deployment manifest changes to cloud-provisioning repo
- [ ] 3.4 Verify ArgoCD syncs the deployment change

## 4. Dev Environment ArgoCD Application Configuration

- [ ] 4.1 Add Image Updater annotations to dev backend ArgoCD Application
- [ ] 4.2 Set image-list annotation with GAR repository path
- [ ] 4.3 Set update-strategy annotation to "latest"
- [ ] 4.4 Set write-back-method annotation to "git"
- [ ] 4.5 Set git-branch annotation to "main"
- [ ] 4.6 Commit Application changes to cloud-provisioning repo
- [ ] 4.7 Verify ArgoCD syncs the Application configuration

## 5. Dev Environment Kustomization Preparation

- [ ] 5.1 Verify dev overlay kustomization uses "latest" tag
- [ ] 5.2 Ensure kustomization images section is properly formatted
- [ ] 5.3 Add comment marker for Image Updater (if needed)
- [ ] 5.4 Commit kustomization changes to cloud-provisioning repo

## 6. Image Updater Functionality Testing

- [ ] 6.1 Trigger backend build by merging PR to main
- [ ] 6.2 Verify GitHub Actions builds and pushes image to GAR with latest tag
- [ ] 6.3 Wait for Image Updater to detect new digest (max 2-3 minutes)
- [ ] 6.4 Verify Image Updater creates commit in cloud-provisioning repo
- [ ] 6.5 Check commit message format includes digest and "build:" prefix
- [ ] 6.6 Verify ArgoCD detects Git change and syncs dev application
- [ ] 6.7 Verify new backend pod is created with updated image
- [ ] 6.8 Check pod uses new digest (kubectl describe pod)
- [ ] 6.9 Verify pod health checks pass and pod reaches Ready state

## 7. Prod Environment Verification (Manual Control)

- [ ] 7.1 Verify prod ArgoCD Application has NO Image Updater annotations
- [ ] 7.2 Verify prod kustomization uses semantic version tag (e.g., v1.0.0)
- [ ] 7.3 Create test GitHub Release in backend repo (e.g., v0.1.0-test)
- [ ] 7.4 Verify Image Updater does NOT update prod kustomization
- [ ] 7.5 Manually update prod kustomization with test version tag
- [ ] 7.6 Commit manual prod update to cloud-provisioning repo
- [ ] 7.7 Verify ArgoCD syncs prod application only after manual commit

## 8. Rollback Testing

- [ ] 8.1 Identify previous working commit in cloud-provisioning repo
- [ ] 8.2 Use ArgoCD UI to rollback dev application to previous sync
- [ ] 8.3 Verify rollback deploys previous image digest
- [ ] 8.4 Test git revert method: revert Image Updater commit
- [ ] 8.5 Verify ArgoCD syncs revert and redeploys previous image
- [ ] 8.6 Clean up test commits (if needed)

## 9. Error Handling and Monitoring

- [ ] 9.1 Test Image Updater behavior when GAR is unreachable (simulate)
- [ ] 9.2 Verify Image Updater logs errors and retries
- [ ] 9.3 Test Image Updater behavior when Git write fails (simulate)
- [ ] 9.4 Verify error logs are accessible via kubectl logs
- [ ] 9.5 Document how to view Image Updater logs for troubleshooting
- [ ] 9.6 Set up log monitoring alert for Image Updater errors (optional)

## 10. Documentation and Runbook

- [ ] 10.1 Update cloud-provisioning README with Image Updater setup info
- [ ] 10.2 Document dev deployment workflow (auto via Image Updater)
- [ ] 10.3 Document prod deployment workflow (manual via Release)
- [ ] 10.4 Create troubleshooting guide for common Image Updater issues
- [ ] 10.5 Document rollback procedures (ArgoCD UI and git revert)
- [ ] 10.6 Add Image Updater configuration to runbook

## 11. Cleanup and Validation

- [ ] 11.1 Remove any temporary test commits from repos
- [ ] 11.2 Verify Image Updater is monitoring correct registry path
- [ ] 11.3 Verify dev and prod environment isolation is maintained
- [ ] 11.4 Review all automated commits follow naming convention
- [ ] 11.5 Confirm imagePullPolicy is set correctly in deployments
- [ ] 11.6 Final smoke test: merge backend PR and verify auto-deployment

## 12. Post-Implementation Monitoring (First Week)

- [ ] 12.1 Monitor Image Updater logs daily for errors
- [ ] 12.2 Track frequency of automated dev deployments
- [ ] 12.3 Verify no unintended prod updates occur
- [ ] 12.4 Check git commit history stays clean and meaningful
- [ ] 12.5 Measure time from backend merge to dev deployment
- [ ] 12.6 Collect feedback on automation workflow
