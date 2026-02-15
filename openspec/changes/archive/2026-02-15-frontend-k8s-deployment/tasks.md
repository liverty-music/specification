## 1. Frontend Repository - Docker Configuration

- [x] 1.1 Create multi-stage Dockerfile in frontend repo root
- [x] 1.2 Configure builder stage using node:22-alpine base image
- [x] 1.3 Configure runtime stage using caddy:2-alpine base image
- [x] 1.4 Copy dist output from builder to /srv in runtime stage
- [x] 1.5 Add .dockerignore file to exclude node_modules, .git, and build artifacts

## 2. Frontend Repository - Caddy Configuration

- [x] 2.1 Create Caddyfile in frontend repo root
- [x] 2.2 Configure Caddy to listen on port 80
- [x] 2.3 Configure root directory as /srv
- [x] 2.4 Enable file_server directive
- [x] 2.5 Add try_files directive for SPA fallback (try_files {path} /index.html)
- [x] 2.6 Update Dockerfile to copy Caddyfile to /etc/caddy/Caddyfile

## 3. Frontend Repository - CI/CD Pipeline

- [x] 3.1 Create .github/workflows/push-image.yaml workflow file
- [x] 3.2 Configure workflow trigger on push to main branch
- [x] 3.3 Add checkout step to clone repository
- [x] 3.4 Add Google Cloud authentication step using workload identity
- [x] 3.5 Add Docker buildx setup step
- [x] 3.6 Add Docker build and push step targeting Google Artifact Registry
- [x] 3.7 Configure image tag using git commit SHA
- [x] 3.8 Set image name as region-docker.pkg.dev/PROJECT_ID/REPO/frontend

## 4. Cloud Provisioning - Frontend Namespace Base

- [x] 4.1 Create k8s/namespaces/frontend/base/ directory
- [x] 4.2 Create base/kustomization.yaml with namespace and commonLabels
- [x] 4.3 Create base/deployment.yaml with frontend app deployment spec
- [x] 4.4 Configure deployment with 1 replica and resource limits (50m/200m CPU, 64Mi/128Mi memory)
- [x] 4.5 Add container image reference (placeholder tag to be overlaid)
- [x] 4.6 Configure container port 80 for Caddy
- [x] 4.7 Add readinessProbe (httpGet on /)
- [x] 4.8 Add livenessProbe (httpGet on /)
- [x] 4.9 Create base/service.yaml with ClusterIP service on port 80
- [x] 4.10 Create base/httproute.yaml with Gateway API HTTPRoute resource
- [x] 4.11 Configure HTTPRoute to reference external-gateway in gateway namespace
- [x] 4.12 Add backendRef pointing to frontend service on port 80

## 5. Cloud Provisioning - Dev Environment Overlay

- [x] 5.1 Create k8s/namespaces/frontend/overlays/dev/ directory
- [x] 5.2 Create overlays/dev/kustomization.yaml referencing base
- [x] 5.3 Add namespace override to 'frontend' in kustomization
- [x] 5.4 Create spot-vm_patch.yaml for nodeSelector/tolerations (follow backend pattern)
- [x] 5.5 Add patch for HTTPRoute hostname to set 'dev.liverty-music.app'
- [x] 5.6 Add patch or configMapGenerator for image tag (if not using Image Updater)

## 6. Cloud Provisioning - ArgoCD Application

- [x] 6.1 Create k8s/argocd-apps/dev/frontend.yaml ArgoCD Application manifest
- [x] 6.2 Configure Application name as 'frontend' in argocd namespace
- [x] 6.3 Set source repoURL to cloud-provisioning GitHub repository
- [x] 6.4 Set source path to k8s/namespaces/frontend/overlays/dev
- [x] 6.5 Set targetRevision to 'main'
- [x] 6.6 Configure destination server as in-cluster (https://kubernetes.default.svc)
- [x] 6.7 Configure destination namespace as 'frontend'
- [x] 6.8 Enable automated sync with prune and selfHeal
- [x] 6.9 Add CreateNamespace=true to syncOptions

## 7. Google Cloud - DNS and Certificate Configuration

- [x] 7.1 Add DNS A record for dev.liverty-music.app pointing to api-gateway-static-ip
- [x] 7.2 Update api-gateway-cert-map to include dev.liverty-music.app domain
- [x] 7.3 Verify certificate provisioning completes successfully

## 8. Deployment and Verification

- [x] 8.1 Commit and push cloud-provisioning changes to main branch
- [x] 8.2 Apply ArgoCD Application to cluster (kubectl apply -f k8s/argocd-apps/dev/frontend.yaml)
- [x] 8.3 Verify ArgoCD syncs frontend namespace successfully
- [x] 8.4 Commit and push frontend repo changes (Dockerfile, Caddyfile, workflow)
- [x] 8.5 Trigger initial image build by pushing to main or running workflow manually
- [x] 8.6 Update frontend deployment image tag to point to built image (if not automated)
- [x] 8.7 Verify frontend pod is running (kubectl get pods -n frontend)
- [x] 8.8 Verify HTTPRoute is bound to Gateway (kubectl get httproute -n frontend)
- [x] 8.9 Access https://dev.liverty-music.app and verify index.html loads
- [x] 8.10 Test SPA routing by accessing a client-side route (e.g., /concerts)
- [x] 8.11 Verify route serves index.html and Aurelia router handles navigation
- [x] 8.12 Check browser network tab for correct cache headers on assets
- [x] 8.13 Verify HTTPS certificate is valid and issued by cert-map
- [x] 8.14 Monitor ArgoCD for sync status and health checks

## 9. Documentation and Cleanup

- [x] 9.1 Document DNS and cert-map setup steps in project runbook
- [x] 9.2 Update README with frontend deployment architecture
- [x] 9.3 Add troubleshooting guide for common issues (pod not starting, routing failures)
- [x] 9.4 Remove any temporary test files or debug configurations
