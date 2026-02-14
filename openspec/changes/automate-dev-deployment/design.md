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
- Maintain GitOps principles (Git as source of truth)
- Preserve manual control for production deployments
- Keep commit history clean and meaningful
- Use digest-based tracking for image immutability

**Non-Goals:**
- Automating production deployments (requires manual approval)
- Changing existing ArgoCD setup significantly
- Implementing progressive delivery (canary/blue-green) at this stage
- Multi-environment orchestration beyond dev/prod

## Decisions

### Decision 1: ArgoCD Image Updater vs. Alternatives

**Choice:** ArgoCD Image Updater

**Rationale:**
- **Native integration**: Official ArgoCD Labs project, designed for ArgoCD ecosystem
- **Digest tracking**: Uses image digests, not just tags, ensuring immutability
- **Git write-back**: Maintains GitOps by committing updates to cloud-provisioning repo
- **Proven solution**: Well-documented, active community ([argocd-image-updater docs](https://argocd-image-updater.readthedocs.io/))

**Alternatives Considered:**
- **Flux CD**: Has built-in image automation, but would require introducing new tooling alongside ArgoCD
- **kubectl rollout restart**: Simpler but breaks GitOps (doesn't update Git), creates Out-of-Sync state
- **Kyverno**: Runtime mutation approach, but lacks visibility (no Git record of what's deployed)

**Trade-off:** Adds one component (Image Updater) but preserves GitOps and ArgoCD-centric workflow.

### Decision 2: Update Strategy (digest vs. latest tag)

**Choice:** Use `latest` tag strategy with digest verification

**Rationale:**
- ArgoCD Image Updater tracks the **digest** behind the tag, not just the tag name
- Prevents cache issues where same tag points to different images
- Automatic commit shows digest change in Git history
- Balances simplicity (latest tag in manifest) with immutability (digest in comments)

**Implementation:**
```yaml
images:
- name: server
  newTag: latest  # Human-readable
  # Updater adds: {"$imagepolicy": "flux-system:backend-policy:tag"}
  # Git commit will show digest: sha256:abc123...
```

### Decision 3: Environment Isolation (dev auto, prod manual)

**Choice:** Separate kustomization overlays with different Image Updater annotations

**Rationale:**
- Dev ArgoCD Application gets Image Updater annotations → automated
- Prod ArgoCD Application has **no** annotations → manual only
- Same base manifests, different overlay behavior
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

### Decision 4: Git Write-Back Method

**Choice:** Direct commit to main branch (no PR)

**Rationale:**
- Solo developer, no review bottleneck
- Automated commits are auditable via commit message format
- ArgoCD auto-sync immediately deploys after commit
- PRs would delay deployment unnecessarily

**Commit Message Format:**
```
build: auto-update backend image to sha256:abc123...

Image Updater detected new digest for asia-northeast2-docker.pkg.dev/.../backend/server:latest
```

**Alternative Considered:** Create PRs for review → Rejected due to solo dev workflow, adds friction

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

### Risk 1: Image Updater Commit Noise
**Risk:** Automated commits every deployment could still clutter history
**Mitigation:**
- Use meaningful commit message template with digest info
- Prefix with `build:` for easy filtering (`git log --invert-grep --grep="^build:"`)
- Consider periodic squash if needed (manual, infrequent)

### Risk 2: Registry Polling Overhead
**Risk:** Image Updater polls GAR every 1-2 minutes, potential rate limits
**Mitigation:**
- Default 2-minute interval is conservative (GAR rate limits are high)
- Can increase interval if needed (`interval: 5m0s`)
- Monitoring via Image Updater logs

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

### Risk 5: Git Write-Back Credentials Management
**Risk:** Image Updater needs Git write access, credential exposure
**Mitigation:**
- Use ArgoCD's existing repo credentials (already has write access)
- RBAC limits Image Updater to specific namespace
- Regularly rotate credentials as per security policy

## Migration Plan

### Phase 1: Installation (Day 1)

1. **Install ArgoCD Image Updater**
   ```bash
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml
   ```

2. **Configure Git write-back**
   - Image Updater uses ArgoCD's existing repo secret
   - Verify write permissions: `kubectl get secret -n argocd argocd-repo-server-tls`

3. **Verify installation**
   ```bash
   kubectl get pods -n argocd | grep image-updater
   kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater
   ```

### Phase 2: Dev Environment Configuration (Day 1)

1. **Add annotations to dev backend ArgoCD Application**
   ```yaml
   annotations:
     argocd-image-updater.argoproj.io/image-list: server=asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/server
     argocd-image-updater.argoproj.io/server.update-strategy: latest
     argocd-image-updater.argoproj.io/write-back-method: git
     argocd-image-updater.argoproj.io/git-branch: main
   ```

2. **Update deployment.yaml imagePullPolicy**
   - Set `imagePullPolicy: Always` in backend deployment

3. **Commit and push**
   - ArgoCD syncs new Application config
   - Image Updater starts monitoring GAR

4. **Test automated update**
   - Merge a PR to backend main
   - GitHub Actions builds and pushes image
   - Wait 2-5 minutes for Image Updater to detect
   - Verify commit in cloud-provisioning repo
   - Verify ArgoCD syncs and deploys new pod

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
1. **Immediate**: Remove annotations from backend Application → stops auto-updates
2. **Temporary**: Pause Image Updater: `kubectl scale deployment argocd-image-updater --replicas=0 -n argocd`
3. **Full rollback**: Delete Image Updater deployment, revert Application annotations
4. **Fallback**: Use `kubectl rollout restart` manually (breaks GitOps but unblocks deployments)

**If bad image deployed to dev:**
1. ArgoCD UI → App History → Rollback to previous sync
2. Or: `git revert <bad-commit>` in cloud-provisioning → ArgoCD re-syncs

## Open Questions

1. **Notification preferences**: Should Image Updater failures send Slack alerts? (Nice-to-have, defer to monitoring setup)
2. **Digest retention**: How long to keep old image digests in GAR? (Defer to GAR cleanup policy, not blocking)
3. **Future multi-service**: If more services added, apply same pattern or centralize? (Cross that bridge when we get there)
