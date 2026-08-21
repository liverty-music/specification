## 1. Specification

- [x] 1.1 Sync the spec delta: apply `MODIFIED Resilient Scheduling on Shared Spot Node Pool` from this change's `specs/zitadel-self-hosted-deployment/spec.md` into `openspec/specs/zitadel-self-hosted-deployment/spec.md` — remove the `(see "Self-healing watchdog auto-restarts a wedged Zitadel API")` cross-reference from the prose, rewrite the L256 paragraph to state that **neither readiness nor liveness detects the wedge** and recovery is **manual rollout restart**, update the Rationale paragraph, and replace the `Wedged-but-ready pod is recovered by the watchdog, not readiness` scenario with `Wedged-but-ready pod requires manual rollout restart`.

## 2. Cloud-Provisioning Cleanup

- [x] 2.1 Remove the stale watchdog comment from `k8s/namespaces/zitadel/overlays/prod/values.yaml` (lines citing the removed `cronjob-watchdog-zitadel.yaml` as the self-healing mechanism). Rewrite the comment to match the current posture: `≥2` replicas bound the blast radius; recovery is `kubectl rollout restart deploy/zitadel-api`.

## 3. Stale Change Dir Removal

- [x] 3.1 Delete `openspec/changes/fix-zitadel-watchdog-slow-wedge-detection/` from the specification repo — it is a byte-identical duplicate of the already-archived `openspec/changes/archive/2026-08-19-fix-zitadel-watchdog-slow-wedge-detection/` and should not exist as an active change.

## 4. Release & Ship

- [x] 4.1 Open a specification PR with the spec sync (1.1) + stale dir removal (3.1); open a cloud-provisioning PR for the comment fix (2.1). Neither touches proto, so no BSR release needed.
- [x] 4.2 Confirm `openspec validate --strict` passes after the spec sync.
- [x] 4.3 Merge both PRs; verify there are no references to the watchdog in `openspec/specs/zitadel-self-hosted-deployment/spec.md` or the active `openspec/changes/` directory.
