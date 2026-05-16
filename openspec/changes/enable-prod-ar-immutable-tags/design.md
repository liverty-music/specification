## Context

The `prepare-prod-service-in` change (cutover landed 2026-05-15, archive pending after §11-§18) established the prod image pipeline: backend + frontend Release-tag-triggered builds push to `liverty-music-prod/{backend,frontend}` AR, and prod kustomize overlays pin to those images by commit SHA (40-char hex). The SHA pin guarantees reproducibility (Pulumi state, AR tag, and the Pulumi-managed GHA workflow all key off the same commit), but it sacrifices the at-a-glance "which version is running" signal that release-tag pinning provides. Operators inspecting `kubectl get pod`, ArgoCD UI, or a `git log` of the prod overlay see opaque hex; they have to query AR (`gcloud artifacts docker images describe ... --format='value(tags)'`) to recover the semver mapping.

The naive fix — switch `newTag: <sha>` to `newTag: v1.0.0` — re-introduces a real risk: Docker tags are mutable. Anyone with `roles/artifactregistry.writer` on the prod repo (including any compromised CI token or operator typo) can re-point `:v1.0.0` to a different digest. Once that happens, ArgoCD's reconciler will not detect drift (manifest still says `v1.0.0`, the image just resolves to different bytes), and prod will silently run a different artifact than the git history claims. GitOps reproducibility relies on the manifest being the unique source of truth; mutable tags undermine that contract.

GCP Artifact Registry has supported `dockerConfig.immutableTags: true` since 2023 (per-repository setting). When enabled:
- The API rejects any `docker push` or `gcloud artifacts docker tags add` that would re-point an existing tag to a different digest, returning 409 Conflict.
- The flag is forward-only: tags written before the flag was enabled remain mutable; only tags written after enablement are locked.
- The flag does NOT prevent tag deletion or new-tag creation; it only blocks the specific re-point-to-different-digest case.

Industry best practice (Kubernetes docs, CIS Kubernetes Benchmark, Google SRE book, Flux's image-automation-controller, ArgoCD Image Updater) recommends pinning to image **digest** (`@sha256:...`) for production. Digest pinning is unforgeable, but it's even more opaque than commit-SHA tags and requires a build/registry roundtrip at PR time to look up the digest after each release. For the current liverty-music scale (single operator, manual release cuts), the immutable-semver-tag approach is the practical compromise that preserves DX while matching the immutability guarantee of digest pinning at the registry boundary.

## Goals / Non-Goals

**Goals:**

- Make prod-running version identifiable at-a-glance from any of: the kustomize overlay diff, `kubectl get deploy/pod -o yaml`, the ArgoCD UI, and Prometheus / log labels.
- Make the prod image reference cryptographically reproducible: once a tag is published to the prod AR, no subsequent operation can re-point it without operator intent (cutting a new patch version).
- Preserve the existing rollback story (flip `newTag:` in overlay, commit, ArgoCD reconciles).
- Document the policy as a runbook so the contract survives operator turnover.

**Non-Goals:**

- Dev AR repos stay mutable. ArgoCD Image Updater on dev needs to overwrite the `:latest` tag on every dev push; immutable-tags would break that flow.
- Staging AR is not in scope (not yet provisioned).
- Image digest pinning (`digest:` field in kustomize, or `image@sha256:...` in manifests) is explicitly NOT chosen — see decision D1 for why.
- Automated semver bumping (Renovate / Dependabot watching the prod AR for new releases and PR'ing the overlay bump) is out of scope. Manual operator-cut releases continue.
- Image signing / cosign / attestations — separate future change.
- Retroactive locking of existing tags pushed before this change applies. The existing `:v1.0.0` tag for backend + frontend stays technically mutable; operationally fine since the next release (`:v1.0.1`) is the first that will exercise the immutability guarantee, and no operator has reason to re-tag historical releases.
- Backend / frontend repo changes — the GHA workflows already push both `:vX.Y.Z` and `:<sha>` tags on Release publish, which is exactly what the policy needs.

## Decisions

### D1: AR Immutable Tags + semver `newTag:` over kustomize `digest:` field

Kustomize supports `digest:` (pin to `image@sha256:...`) as an alternative to `newTag:`. Digest pinning is the gold standard per K8s docs and CIS Benchmark 5.7.1: cryptographically unforgeable, no registry IAM dependency, no ambiguity. Why not choose it?

- **DX cost at PR time**: digest is only knowable after the image is built and pushed. The operator workflow becomes: cut Release → wait for GHA → look up digest via `gcloud artifacts docker images describe ... --format='value(image)'` → paste digest into overlay PR. Versus the immutable-tag flow: cut Release → bump `newTag: v1.0.1` in overlay PR. The latter is faster, less error-prone, and matches operator mental model.
- **Manifest readability**: `digest: sha256:abcd1234...` is no better than the current `newTag: 3bc2dada...` it replaces. `newTag: v1.0.0` is significantly more legible.
- **Equivalent security guarantee at the boundary that matters**: digest pinning blocks the attacker who has compromised the AR write IAM (because they cannot re-create the same digest with different content). Immutable-tags also blocks this attacker (because they cannot re-point the tag). Both guarantees collapse if AR itself is compromised — but the threat model where AR is compromised is not bounded by manifest pinning style; it requires registry-level controls.

Alternative considered: hybrid (`newTag: v1.0.0` + `digest: sha256:...` in same overlay entry). Kustomize doesn't support both fields simultaneously on a single image entry. Rejected.

Alternative considered: pin to combined tag `v1.0.0-3bc2dada` (build pipeline pushes a third tag). Rejected — adds a workflow change with no security benefit over immutable-semver-tag, and the combined tag is no more readable than `v1.0.0` alone.

### D2: Dev AR stays mutable; any other env (incl. future staging) gets immutable-tags by default

ArgoCD Image Updater on dev rewrites the `:latest` and `:main` tags on every push to `liverty-music/{backend,frontend}:main`. Enabling immutable-tags on dev AR would break this — `:latest` would have to be deleted and recreated on every push, which is not how Image Updater works. The cost-benefit: dev exists to be churned; immutability there has zero operational value.

Pulumi scope: `dockerConfig.immutableTags = true` is set on every stack EXCEPT dev (i.e., the conditional is `environment !== 'dev'`, not `environment === 'prod'`). This is intentionally fail-secure: any future non-dev environment (staging when it gets provisioned, any prod-replica, etc.) automatically inherits the immutable-tags policy without needing a follow-up change. Listing prod by name would force every future env to opt in via explicit code change, with the failure mode of "operator forgets, env runs with mutable tags". The negative-form conditional makes the secure case the default.

Today only dev and prod stacks exist; staging is documented as a future possibility (per the workspace CLAUDE.md). When staging is provisioned, its AR repos will be created with `immutableTags: true` automatically.

### D3: Always pin (no `:latest` even on prod)

The `:latest` tag has the additional pathology that Pod restarts can silently pull different image bytes without any manifest change. This is the original sin that GitOps was designed to eliminate. Even if `:latest` were immutable, the manifest-as-source-of-truth principle still forbids it on prod. The kustomize overlay must always reference a fixed semver.

### D4: Migration order: Pulumi first, then overlay, then validate on next release

1. Open one PR on `liverty-music/cloud-provisioning` that bundles: (a) Pulumi `dockerConfig.immutableTags = true` on prod backend + frontend AR repos, (b) kustomize overlay rewrites (4 backend + 1 frontend `newTag:` from SHA to `v1.0.0` with SHA in comment), (c) `app.kubernetes.io/version` label patches, (d) the new runbook. Single PR keeps the cutover atomic.
2. After merge: operator triggers `pulumi up --stack prod` via Pulumi Cloud console. AR config changes are no-op for existing tags but lock all future writes.
3. ArgoCD detects the kustomize change and rolls the Deployments with the new `image:` and `metadata.labels`. The image bytes are unchanged (same digest, just referenced by a different tag name), so Pods restart but no functional behavior changes.
4. Operationally validate by cutting a no-op test release (`v1.0.1` for one of backend or frontend, with a no-functional-change commit), confirming AR accepts the initial `v1.0.1` push and would reject a hypothetical second `v1.0.1` push attempt.

Ordering matters: if the overlay rewrite landed before AR was set to immutable-tags, there would be a brief window where the new `:v1.0.0` reference works but isn't yet locked. In practice, no one is racing to re-tag during a deployment window, so the risk is theoretical, but bundling in a single PR + applying Pulumi-before-ArgoCD-sync keeps the invariant clean.

### D5: Preserve commit SHA in comment, propagate version via Recommended Label

Forensics use cases (incident response, compliance audit, security review) need the source commit, not just the semver. Two channels:

- Kustomize overlay: inline comment `newTag: v1.0.0  # commit 3bc2dada3c4cd06c218235eb7fe21ad638e29bf3` — survives in git history, queryable via `git blame` on the overlay.
- Runtime: add `app.kubernetes.io/version: "1.0.0"` Recommended Label on the Deployment / CronJob (per Kubernetes conventions). This propagates to Pods, gets scraped by Prometheus relabeling (`__meta_kubernetes_pod_label_app_kubernetes_io_version`), and lands in log entries via the OTel resource processor.

The label could also carry the SHA (`app.kubernetes.io/version: "1.0.0-3bc2dada"`), but per Kubernetes label-value constraints (63 chars, DNS-1123) and convention (`version: <semver>`), keep the label semver-only and rely on the comment for SHA trace.

### D6: GHA push idempotency under immutable-tags

The backend `deploy.yml` and frontend `push-image.yaml` workflows push BOTH `:vX.Y.Z` and `:<sha>` tags on every Release publish. The push is implemented via `docker/build-push-action@v5` with `push: true` and `tags: <tag1>,<tag2>`. Under immutable-tags:

- First-time push of `:v1.0.0` + `:<sha>` for a fresh Release: both pushes succeed. AR locks both tags.
- Re-run of a Release that already succeeded (operator re-publishes the same GH Release, GHA re-fires): the second push attempt of `:v1.0.0` would return 409 Conflict. The workflow step fails. **This is the intended enforcement** — silent overwrite would defeat the entire policy.

Operator playbook for re-run scenarios: if the original release content is correct but the Release notes need fixing, edit Release notes only (no re-run). If the release content needs to change (a bad release that needs a fix), cut a new patch version (`v1.0.1`). Document in the runbook.

### D7: Rollback unchanged

Today's rollback: flip `newTag: <sha-new>` → `newTag: <sha-old>` in overlay PR. Tomorrow's rollback: flip `newTag: v1.0.5` → `newTag: v1.0.4` in overlay PR. Same workflow, more readable diff. Immutable-tags has no effect on rollback because rollback targets a previously-published (already-immutable) tag.

## Risks / Trade-offs

- **R1: Retroactive locking confusion** → Operator might assume enabling `immutableTags: true` retroactively locks the existing `:v1.0.0` tag. It does NOT — only tags written after the flag is enabled. Mitigation: explicit note in the runbook + this design doc. Practical impact: zero, because no one re-tags historical releases in the current ops model.
- **R2: Accidental enablement on dev AR** → Would break ArgoCD Image Updater (dev's `:latest` rewrite). Mitigation: Pulumi code applies `immutableTags = true` only inside the prod-stack branch of the `Repository` resource construction; dev-stack call site leaves the option unset (default `false`). The PR review SHALL eyeball this.
- **R3: GHA push 409 Conflict surfacing as a failed run for legitimate re-runs** → If an operator legitimately wants to re-run a release for non-content reasons (e.g., the GHA infrastructure flaked mid-run), the second push attempt fails. Mitigation: GHA's `docker/build-push-action` is idempotent when the digest matches an existing tag — it short-circuits the push. If the digest differs (rebuild produced different bytes due to non-determinism), AR rejects with 409, which is the correct outcome (don't silently swap prod under a stable tag). Operator escalation path: cut a new patch version.
- **R4: Operator typos in manual `gcloud artifacts docker tags add`** → If an operator manually re-points a tag for debugging (e.g., trying to "fix" v1.0.0 mid-incident), the API rejects. Mitigation: runbook explicitly documents that recovery is "cut v1.0.1", not "re-tag v1.0.0".
- **R5: Pulumi state drift on AR repo resources during this apply** → Recent history (the WIF binding gap on prod that surfaced during `prepare-prod-service-in` §5) suggests prod state has had silent drift from manual ops. If the AR repos have drift, `pulumi preview --stack prod` might show more than the expected 2 updates (`backend` repo + `frontend` repo). Mitigation: PR description documents the expected preview shape, operator reviews any extra deltas before applying.

## Migration Plan

Per D4: single PR on `liverty-music/cloud-provisioning` bundles all changes.

1. **PR**: Pulumi `dockerConfig.immutableTags = true` on prod backend + frontend AR repos + kustomize overlay rewrites (SHA → semver `newTag:`) + `app.kubernetes.io/version` patches + runbook. Merge after CI green + review.
2. **Pulumi apply**: operator triggers `pulumi up --stack prod` via Pulumi Cloud console after merge. Expected preview: 2 `gcp:artifactregistry/repository:Repository` updates with `dockerConfig.immutableTags` field changing `false` → `true`.
3. **ArgoCD reconcile**: automatic on the cloud-provisioning main-branch change. Prod Deployments / CronJobs roll with new `image:` reference (same digest) and new `metadata.labels` (adds `app.kubernetes.io/version`).
4. **Validation**: verify `gcloud artifacts repositories describe backend --project=liverty-music-prod --location=asia-northeast2 --format='value(dockerConfig.immutableTags)'` returns `True` for both repos. Verify `kubectl get deploy -A -o yaml | grep image:` on prod shows `:v1.0.0` everywhere. Verify `kubectl get deploy -A --show-labels | grep app.kubernetes.io/version` shows the label.
5. **Operational validation (optional, after this change archives)**: cut a no-op test patch release (`v1.0.1`) to confirm the end-to-end loop: Release publish → AR push of `:v1.0.1` + `:<new-sha>` → AR locks both tags → overlay PR bumps `newTag: v1.0.0` → `newTag: v1.0.1` → ArgoCD rolls.

**Rollback**: revert the cloud-provisioning PR (or, more granularly, revert just the Pulumi change to flip `immutableTags` back to `false`). The kustomize overlay rewrite is independently revertible — flipping `newTag: v1.0.0` back to the original SHA works any time and would re-issue a no-op rollout (same digest under the SHA tag, which still exists in AR).
