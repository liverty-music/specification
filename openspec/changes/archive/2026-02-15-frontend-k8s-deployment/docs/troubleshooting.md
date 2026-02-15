# Frontend Kubernetes Deployment Troubleshooting Guide

This guide covers common issues when deploying the Aurelia 2 frontend to Kubernetes.

## Pod Issues

### Pod not starting (ImagePullBackOff)

**Symptoms**:
```bash
$ kubectl get pods -n frontend
NAME                       READY   STATUS             RESTARTS   AGE
web-app-xxx-yyy            0/1     ImagePullBackOff   0          2m
```

**Causes & Solutions**:

1. **Missing IAM permissions**
   - **Check**: Does the GKE node service account have `artifactregistry.reader` role?
   - **Fix**: Verify IAM bindings exist:
     ```bash
     gcloud artifacts repositories get-iam-policy frontend \
       --location=asia-northeast2 \
       --project=liverty-music-dev
     ```
   - **Expected**: Service account `gke-node@liverty-music-dev.iam.gserviceaccount.com` should have `roles/artifactregistry.reader`
   - **Fix in Pulumi**: Ensure `frontend-gke-node-x-artifact-registry-reader` binding exists in `src/gcp/components/kubernetes.ts`

2. **Image doesn't exist**
   - **Check**: Does the image exist in Artifact Registry?
     ```bash
     gcloud artifacts docker images list asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/app
     ```
   - **Fix**: Trigger image build by pushing to frontend repository main branch or running GitHub Actions workflow manually

3. **Wrong image reference**
   - **Check**: Verify deployment image reference matches registry:
     ```bash
     kubectl get deployment -n frontend web-app -o jsonpath='{.spec.template.spec.containers[0].image}'
     ```
   - **Expected**: `asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/app:<tag>`
   - **Fix**: Update `k8s/namespaces/frontend/base/web/deployment.yaml` or kustomization image override

### Pod crashing (CrashLoopBackOff)

**Symptoms**:
```bash
$ kubectl get pods -n frontend
NAME                       READY   STATUS             RESTARTS   AGE
web-app-xxx-yyy            0/1     CrashLoopBackOff   5          5m
```

**Diagnosis**:
```bash
# Check pod logs
kubectl logs -n frontend deployment/web-app

# Check pod events
kubectl describe pod -n frontend <pod-name>
```

**Common Causes**:

1. **Caddy configuration error**
   - **Check logs** for Caddyfile syntax errors
   - **Verify**: `Caddyfile` is mounted at `/etc/caddy/Caddyfile`
   - **Test locally**: Build and run Docker image locally to reproduce

2. **Missing static assets**
   - **Check**: Is `/srv` directory empty in container?
   - **Verify**: Dockerfile copies built assets: `COPY --from=builder /app/dist /srv`
   - **Fix**: Rebuild frontend image with correct build output

3. **Port conflict**
   - **Check**: Is Caddy listening on port 80?
   - **Verify**: Container port matches service port (both should be 80)

### Pod ready but not serving traffic

**Symptoms**:
- Pod shows `1/1 Running` but `curl <pod-ip>` fails
- Service has no endpoints

**Diagnosis**:
```bash
# Check pod IP and test directly
POD_IP=$(kubectl get pod -n frontend -l app=web -o jsonpath='{.items[0].status.podIP}')
curl -I http://$POD_IP/

# Check service endpoints
kubectl get endpoints -n frontend web-svc
```

**Causes & Solutions**:

1. **Readiness probe failing**
   - **Check pod events**: `kubectl describe pod -n frontend <pod-name>`
   - **Look for**: "Readiness probe failed" messages
   - **Fix**: Ensure Caddy is serving on port 80 and `/` returns 200 OK

2. **Wrong service selector**
   - **Check**: Service selector matches deployment labels
   - **Verify**:
     ```bash
     kubectl get svc -n frontend web-svc -o yaml | grep -A 3 selector
     kubectl get deployment -n frontend web-app -o yaml | grep -A 3 labels
     ```
   - **Fix**: Update service selector in `k8s/namespaces/frontend/base/web/service.yaml`

## HTTPRoute Issues

### HTTPRoute not binding to Gateway

**Symptoms**:
```bash
$ kubectl get httproute -n frontend
NAME        HOSTNAMES                     AGE
web-route   ["dev.liverty-music.app"]     5m

$ kubectl describe httproute -n frontend web-route
# Conditions show Accepted: False or ResolvedRefs: False
```

**Causes & Solutions**:

1. **Gateway doesn't exist**
   - **Check**: Gateway exists in `gateway` namespace
     ```bash
     kubectl get gateway -n gateway external-gateway
     ```
   - **Fix**: Ensure Gateway API resources are deployed (shared with backend)

2. **Wrong Gateway reference**
   - **Check HTTPRoute spec**:
     ```bash
     kubectl get httproute -n frontend web-route -o yaml | grep -A 5 parentRefs
     ```
   - **Expected**: `name: external-gateway`, `namespace: gateway`
   - **Fix**: Update `k8s/namespaces/frontend/base/web/httproute.yaml`

3. **Cross-namespace reference not allowed**
   - **Check**: ReferenceGrant exists allowing frontend→gateway reference
   - **Note**: GKE Gateway API typically allows cross-namespace by default
   - **Fix**: If needed, create ReferenceGrant resource

### HTTPRoute bound but returning 404

**Symptoms**:
- HTTPRoute shows `Accepted: True`, `ResolvedRefs: True`
- Accessing `https://dev.liverty-music.app` returns 404

**Diagnosis**:
```bash
# Check HTTPRoute status
kubectl describe httproute -n frontend web-route

# Check if hostname conflicts with other HTTPRoutes
kubectl get httproute -A
```

**Causes & Solutions**:

1. **Hostname conflict**
   - **Check**: Multiple HTTPRoutes using same hostname
   - **Fix**: Ensure hostnames are unique across namespaces

2. **Backend service doesn't exist**
   - **Check**:
     ```bash
     kubectl get svc -n frontend web-svc
     kubectl get endpoints -n frontend web-svc
     ```
   - **Fix**: Ensure service exists and has endpoints

3. **Wrong backend reference in HTTPRoute**
   - **Check**: HTTPRoute backendRefs points to correct service
   - **Expected**: `name: web-svc`, `port: 80`
   - **Fix**: Update `k8s/namespaces/frontend/base/web/httproute.yaml`

## TLS Certificate Issues

### Certificate not provisioned

**Symptoms**:
- Accessing `https://dev.liverty-music.app` shows certificate error
- Browser shows "Not Secure" or certificate mismatch

**Diagnosis**:
```bash
# Check certificate status
gcloud certificate-manager certificates describe api-gateway-cert \
  --location=global \
  --project=liverty-music-dev

# Check certificate map
gcloud certificate-manager maps entries list \
  --map=api-gateway-cert-map \
  --location=global \
  --project=liverty-music-dev
```

**Causes & Solutions**:

1. **Certificate map entry missing**
   - **Check**: Entry exists for `dev.liverty-music.app`
   - **Expected**: `web-app-cert-map-entry` mapping hostname to certificate
   - **Fix in Pulumi**: Ensure `CertificateMapEntry` resource exists in `src/gcp/components/network.ts`

2. **DNS authorization not complete**
   - **Check**: DNS CNAME records for ACME challenge exist
   - **Verify**: `dig _acme-challenge.dev.liverty-music.app CNAME`
   - **Fix**: Wait for DNS propagation (up to 24 hours), or check Pulumi DNS resources

3. **Certificate not including frontend domain**
   - **Check**: Certificate managed domains include `dev.liverty-music.app`
   - **Fix in Pulumi**: Update certificate `managedDomains` list

### Wrong certificate served

**Symptoms**:
- HTTPS works but shows certificate for wrong domain (e.g., `*.google.com`)

**Diagnosis**:
```bash
echo | openssl s_client -servername dev.liverty-music.app -connect dev.liverty-music.app:443 2>/dev/null | openssl x509 -noout -text | grep -E "(Subject|DNS)"
```

**Causes & Solutions**:

1. **Certificate map not attached to Gateway**
   - **Check**: Gateway has certificate map annotation
   - **Expected**: Gateway should reference `api-gateway-cert-map`
   - **Fix**: Verify Gateway configuration (shared with backend)

2. **Hostname not in certificate SANs**
   - **Check**: Certificate Subject Alternative Names include `dev.liverty-music.app`
   - **Fix**: Update certificate to include frontend domain

## SPA Routing Issues

### Client-side routes return 404

**Symptoms**:
- Root path (`/`) loads fine
- Navigating to `/concerts` returns 404
- Direct access to `https://dev.liverty-music.app/concerts` fails

**Diagnosis**:
```bash
# Test if route fallback is working
curl -I https://dev.liverty-music.app/concerts

# Expected: HTTP 200 with index.html
# Actual (if broken): HTTP 404
```

**Causes & Solutions**:

1. **Caddyfile missing try_files directive**
   - **Check**: Caddyfile contains `try_files {path} /index.html`
   - **Verify**:
     ```bash
     kubectl get configmap -n frontend web-caddyfile -o yaml
     ```
   - **Fix**: Update `frontend/Caddyfile` in frontend repository and rebuild image

2. **Static assets being affected by fallback**
   - **Symptom**: JavaScript files return HTML instead of JS
   - **Check**: Assets like `/assets/index-*.js` return correct content-type
   - **Fix**: Ensure `try_files` checks for file existence before fallback

## ArgoCD Sync Issues

### ArgoCD not syncing changes

**Symptoms**:
- Changes pushed to cloud-provisioning repository
- ArgoCD Application shows "OutOfSync" but not syncing

**Diagnosis**:
```bash
# Check Application status
kubectl get application -n argocd frontend -o yaml

# Check ArgoCD logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller
```

**Causes & Solutions**:

1. **Auto-sync disabled**
   - **Check**: Application has `automated: {}` in syncPolicy
   - **Fix**: Update `k8s/argocd-apps/dev/frontend.yaml` to enable auto-sync

2. **Sync hook failure**
   - **Check**: ArgoCD Application status for errors
   - **Fix**: Review hook logs and fix issues

3. **Kustomize build error**
   - **Check**: ArgoCD can build manifests
   - **Test locally**:
     ```bash
     kustomize build k8s/namespaces/frontend/overlays/dev
     ```
   - **Fix**: Correct kustomization.yaml syntax errors

### ArgoCD shows "Degraded" health

**Symptoms**:
- Application synced but health status is "Degraded"

**Diagnosis**:
```bash
# Check Application health details
kubectl get application -n argocd frontend -o jsonpath='{.status.health.message}'
```

**Causes & Solutions**:

1. **Pod not ready**
   - **See**: Pod Issues section above

2. **Service has no endpoints**
   - **Check**: `kubectl get endpoints -n frontend`
   - **Fix**: Ensure pods are running and match service selector

## DNS Issues

### Domain not resolving

**Symptoms**:
```bash
$ dig dev.liverty-music.app
# Returns NXDOMAIN or no A record
```

**Diagnosis**:
```bash
# Check DNS A record in GCP
gcloud dns record-sets list --zone=<zone-name> --filter="name:dev.liverty-music.app"
```

**Causes & Solutions**:

1. **DNS record not created**
   - **Check**: Pulumi created A record resource
   - **Fix in Pulumi**: Ensure `web-app-a-record` resource exists in `src/gcp/components/network.ts`

2. **Wrong DNS zone**
   - **Check**: A record created in correct public zone
   - **Verify**: Zone matches backend DNS records

3. **DNS propagation delay**
   - **Wait**: DNS changes can take up to 24 hours to propagate
   - **Test**: Use `dig @8.8.8.8 dev.liverty-music.app` to query Google DNS directly

## GitHub Actions CI/CD Issues

### Image build failing

**Symptoms**:
- GitHub Actions workflow fails on image build step

**Diagnosis**:
- Check workflow run logs in GitHub Actions UI

**Common Causes**:

1. **Workload Identity Federation auth failure**
   - **Error**: "Permission denied" or "Authentication failed"
   - **Check**: WIF binding exists for frontend repository
   - **Fix in Pulumi**: Ensure `github-actions-frontend-wif-user` binding exists

2. **npm install or build failure**
   - **Check**: Dependencies are correct in package.json
   - **Fix**: Test build locally, update dependencies

3. **Docker build context error**
   - **Check**: Dockerfile is in repository root
   - **Verify**: .dockerignore doesn't exclude required files

## Performance Issues

### Slow initial page load

**Diagnosis**:
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://dev.liverty-music.app
```

**Causes & Solutions**:

1. **Large bundle size**
   - **Check**: Asset sizes in `/assets/`
   - **Fix**: Optimize Vite build, enable code splitting

2. **No caching headers**
   - **Check**: Cache-Control headers on assets
   - **Fix**: Configure Caddy to set appropriate cache headers

3. **Pod resource limits too low**
   - **Check**: Pod CPU/memory throttling
   - **Fix**: Increase resource limits in deployment.yaml

## Getting More Help

- **ArgoCD UI**: Port-forward and access at http://localhost:8080
  ```bash
  kubectl port-forward svc/argocd-server -n argocd 8080:80
  ```
- **GKE Console**: https://console.cloud.google.com/kubernetes
- **Logs**: `kubectl logs -n frontend deployment/web-app --tail=100`
- **Events**: `kubectl get events -n frontend --sort-by='.lastTimestamp'`
