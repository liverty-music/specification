## Context

**Current State:**
- Backend images are built and pushed to GAR via GitHub Actions on every main branch merge
- Images are tagged with both `latest` and commit SHA (`${GITHUB_SHA}`)
- Dev deployment requires manual kustomization updates in cloud-provisioning repo
- Multiple merges per day create repetitive "update image tag" commits

**Environment Structure:**
- **Dev**: Requires automated deployment, uses `latest` tag, high update frequency (multiple times daily)
- **Prod**: Requires manual control via GitHub Releases, uses semantic versioning (v1.2.3)

**Constraints:**
- Solo developer workflow
- ArgoCD already deployed for GitOps
- Cloud-provisioning repo is source of truth for k8s manifests
- Need to avoid commit history pollution in dev

## Goals / Non-Goals

**Goals:**
- Automate dev environment deployments without manual kustomization updates
- Keep commit history clean and meaningful (zero automated commits)
- Preserve manual control for production deployments
- Use digest-based tracking for image immutability
- Keep the solution entirely in-cluster (no external kubectl access needed)

**Non-Goals:**
- Automating production deployments (requires manual approval)
- Changing existing ArgoCD setup significantly
- Implementing progressive delivery (canary/blue-green) at this stage
- Multi-environment orchestration beyond dev/prod
- Strict GitOps compliance for dev environment (acceptable trade-off for clean history)

## Decisions

### Decision 1: ArgoCD Image Updater with `argocd` Write-Back Method

**Choice:** ArgoCD Image Updater using the `argocd` write-back method (Application parameter overrides, no Git commits)

**Rationale:**
- **Zero commit spam**: The `argocd` write-back method updates ArgoCD Application parameter overrides directly, without committing to Git
- **Native ArgoCD integration**: Official ArgoCD Labs project, operates through ArgoCD's own API
- **No drift conflict**: ArgoCD treats parameter overrides as legitimate desired-state changes
- **No external access needed**: Runs entirely in-cluster, no GitHub Actions kubectl permissions required
- **Digest tracking**: Detects image digest changes behind the `latest` tag

**How it works:**
1. Image Updater polls GAR for digest changes on `latest` tag
2. When a new digest is detected, it calls the ArgoCD API
3. ArgoCD Application's `.spec.source.kustomize.images` is updated via parameter override
4. ArgoCD detects the Application spec change and syncs automatically
5. New pods are created with the updated image

**Alternatives Considered:**
- **ArgoCD Image Updater (git write-back)**: GitOps compliant but creates commit spam (one commit per image update), contradicting the primary goal of clean commit history
- **Flux CD Image Automation**: Built-in image automation but always writes to Git. Also introduces a second GitOps tool alongside ArgoCD
- **kubectl rollout restart (GitHub Actions)**: Zero commits but requires granting GKE access to the CI service account, expanding the external attack surface
- **Keel**: Patches Deployments directly, causing fatal ArgoCD drift conflicts (selfHeal reverts changes)
- **Kargo**: Supports `argocd-update` without Git, but is a heavy platform (own API server, controller, UI, CRDs) -- overkill for this use case
- **Kyverno**: Runtime mutation lacks visibility and breaks GitOps principles

**Trade-off:** Dev environment is not strictly GitOps (deployed state is not recorded in Git). This is acceptable because:
- Dev environment can tolerate temporary inconsistency
- Image Updater re-applies overrides within 30s if Application is recreated
- Production will use Git-backed deployment (manual updates)

### Decision 2: Update Strategy

**Choice:** Use `latest` tag strategy with digest verification

**Rationale:**
- ArgoCD Image Updater tracks the **digest** behind the tag, not just the tag name
- Prevents cache issues where same tag points to different images
- Balances simplicity (latest tag in manifest) with immutability (digest tracking)

### Decision 3: Environment Isolation (dev auto, prod manual)

**Choice:** Separate ArgoCD Application annotations per environment

**Rationale:**
- Dev ArgoCD Application gets Image Updater annotations → automated
- Prod ArgoCD Application has **no** annotations → manual only
- Same base manifests, different automation behavior
- Clear separation of automation policy per environment

**Structure:**
```
k8s/namespaces/backend/
├── base/                    # Shared config
├── overlays/
│   ├── dev/
│   │   └── kustomization.yaml  # latest tag, Image Updater enabled
│   └── prod/
│       └── kustomization.yaml  # v1.2.3 tag, no Image Updater
```

### Decision 4: Polling Interval

**Choice:** 30-second polling interval

**Rationale:**
- Faster detection of new images (default is 2 minutes)
- GAR API quota is well within limits (3 images × 2 calls/min = ~8,640 calls/day)
- No additional cost (GAR API calls are within standard project quota)
- Combined with CI build time (~2-3 min), total deploy latency is ~3-3.5 minutes

**Configuration:**
```
--interval 30s
```

### Decision 5: imagePullPolicy Configuration

**Choice:** Set `imagePullPolicy: Always` for dev deployments

**Rationale:**
- Kubernetes best practice for `latest` tags ([K8s docs](https://kubernetes.io/docs/concepts/containers/images/))
- Ensures kubelet always checks registry for digest changes
- Still uses local cache if digest matches (no unnecessary pulls)
- Mitigates edge cases where tag is reused

**Implementation:**
```yaml
# deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: server
        image: server:latest
        imagePullPolicy: Always
```

## Risks / Trade-offs

### Risk 1: Application Recreation Loses Parameter Overrides
**Risk:** If the ArgoCD Application resource is recreated (e.g., root-app sync, disaster recovery), the image parameter overrides are lost and pods temporarily revert to the image specified in Git.
**Mitigation:**
- Image Updater re-detects the latest digest within 30 seconds and re-applies the override
- Downtime is minimal (30s polling + ArgoCD sync time)
- This only affects dev environment; prod uses Git-based image tags
- Application recreation is rare (manual root-app sync, ArgoCD upgrade)

### Risk 2: No Git Audit Trail for Dev Deployments
**Risk:** Since nothing is committed to Git, there is no Git history of which image version was deployed to dev and when.
**Mitigation:**
- Image Updater logs record all update operations
- ArgoCD Application history shows sync events with image details
- `kubectl describe pod` shows current image digest
- For dev environment, operational observability is sufficient; formal audit trail is not required

### Risk 3: Deployment Failures Not Caught Early
**Risk:** Auto-deployment might push broken images to dev
**Mitigation:**
- Backend CI runs tests before building image
- GKE health checks will fail pod deployment if broken
- ArgoCD shows deployment status, easy to rollback
- **Future**: Add Argo Rollouts for canary deployments (out of scope now)

### Risk 4: Prod Manual Process Skipped by Accident
**Risk:** Developer might forget to manually update prod after release
**Mitigation:**
- Prod Application has **no** Image Updater annotations (can't auto-update)
- GitHub Release checklist includes "update cloud-provisioning prod overlay"
- ArgoCD will show Out-of-Sync if prod manifest not updated

## Migration Plan

### Phase 1: Installation (Day 1)

1. **Install ArgoCD Image Updater**
   - Add Kustomize manifests to `k8s/namespaces/argocd/` for GitOps-managed installation
   - Configure `--interval 30s` flag

2. **Verify installation**
   ```bash
   kubectl get pods -n argocd | grep image-updater
   kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater
   ```

### Phase 2: Dev Environment Configuration (Day 1)

1. **Add annotations to dev ArgoCD Applications (backend, frontend)**
   ```yaml
   annotations:
     argocd-image-updater.argoproj.io/image-list: server=asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server
     argocd-image-updater.argoproj.io/server.update-strategy: latest
     # write-back-method defaults to "argocd" (no Git writes)
   ```

2. **Update deployment.yaml imagePullPolicy**
   - Set `imagePullPolicy: Always` in backend and frontend deployments

3. **Commit and push**
   - ArgoCD syncs new Application config and Image Updater deployment
   - Image Updater starts monitoring GAR

4. **Test automated update**
   - Merge a PR to backend main
   - GitHub Actions builds and pushes image
   - Wait ~30s-1min for Image Updater to detect
   - Verify ArgoCD Application shows updated image in parameter overrides
   - Verify new pod is running with updated digest

### Phase 3: Production Workflow (Day 2)

1. **Document prod release process**
   - Create GitHub Release in backend repo (v1.2.3)
   - Manually update prod overlay kustomization.yaml
   - Commit: `release: deploy backend v1.2.3 to prod`
   - ArgoCD syncs prod (manual or auto, depending on syncPolicy)

2. **Test prod release**
   - Create test release v0.1.0
   - Follow manual workflow
   - Verify no Image Updater interference

### Rollback Strategy

**If Image Updater causes issues:**
1. **Immediate**: Remove annotations from Application → stops auto-updates
2. **Temporary**: Pause Image Updater: `kubectl scale deployment argocd-image-updater --replicas=0 -n argocd`
3. **Full rollback**: Delete Image Updater deployment, revert Application annotations

**If bad image deployed to dev:**
1. ArgoCD UI → App History → Rollback to previous sync
2. Or: manually set image override via `argocd app set` to a known-good digest

## Open Questions

1. **Notification preferences**: Should Image Updater failures send Slack alerts? (Nice-to-have, defer to monitoring setup)
2. **Digest retention**: How long to keep old image digests in GAR? (Defer to GAR cleanup policy, not blocking)
3. **Future multi-service**: If more services added (concert-discovery, web-app), apply same annotation pattern per Application
