# SUPERSEDED

**This change was abandoned, not completed.** It was merged (PR [liverty-music/specification#468](https://github.com/liverty-music/specification/pull/468)) but **never deployed to prod Pulumi state**.

## Supersession

Replaced by [`refactor-unify-env-dispatch`](../refactor-unify-env-dispatch/) (archived alongside this directory).

- **Date**: 2026-05-15
- **Superseded by spec PR**: [liverty-music/specification#470](https://github.com/liverty-music/specification/pull/470) (commit `ca02eed`)
- **Superseded by implementation PR**: [liverty-music/cloud-provisioning#262](https://github.com/liverty-music/cloud-provisioning/pull/262) (merge commit `7fd969e`)
- **Prod Pulumi update version**: v157 (succeeded 2026-05-15T07:36:39Z, see [deployment 265](https://app.pulumi.com/pannpers/liverty-music/prod/deployments/265))

## Status of tasks below

Tasks marked `[ ]` in this change's [tasks.md](./tasks.md) were **not performed**. The `[ ]` markers are preserved (NOT fake-checked as `[x]`) to keep the audit trail honest about what was abandoned.

## What replaced it

`complete-zitadel-prod-pulumi-stack` proposed the 9-component prod Zitadel gap closure via a new `ZitadelProdStackComponent` wrapper class parallel to dev's `Zitadel` class. The implementation merged in cloud-provisioning#260 + #261.

`refactor-unify-env-dispatch` retrospectively rejected the parallel-class pattern (architectural anti-pattern: ~600 lines of duplicated component wiring between dev's `Zitadel` and prod's `ZitadelProdStackComponent`). The replacement delivered the same 9-component gap closure by:

1. Deleting `ZitadelProdStackComponent` + `BackendMachineKeyComponent` entirely.
2. Removing the `env !== 'dev'` throw guard from the existing dev `Zitadel` class.
3. Sourcing per-env values (admin org id, redirect URIs, sender address, cluster name/location for monitoring) from `Record<Environment, T>` constant maps.
4. Inline `import:` resource option on the `zitadel.Org('admin', ...)` for the prod admin org id, replacing the planned CLI `pulumi import` step.

End-state operational outcome is identical: prod operator Console sign-in via Google IdP, prod backend ↔ Zitadel JWT auth, prod ESO-mirrored login PAT for `zitadel-web` Pod. The route to get there is simpler (15 files changed, -641 net lines vs. the original ~370-line `ZitadelProdStackComponent` + ~210-line `BackendMachineKeyComponent`).

## Why this abandonment was the right call (pre-launch architecture cleanup)

The user explicit framing at the time of the pivot:
> *破壊的な変更をするのはサービスイン前のこのタイミングが最適です*

Combined with the [devil's advocate adversarial review](https://github.com/liverty-music/specification/pull/470) that surfaced C1-C10 concerns about the parallel-class pattern, the abandonment was a deliberate pre-launch architecture correction — not a project-management failure.

## Historical reference value

The `proposal.md` + `design.md` of this change document the discovery / debugging chain that led to the unified-class insight: the `pulumi import` CLI chicken-and-egg (hotfix #261 introduced `import:` resource option as a workaround), the wrong redirect URI mismatch (`/ui/v2/login/login/callback` vs the canonical `/idps/callback`), the `pulumiJwtProfileJson` ESC fabrication, etc. Future contributors revisiting any of these decisions should read the artifacts as case studies in how the parallel-class pattern complicated reasoning across two near-identical class definitions.

The spec delta in [specs/zitadel-self-hosted-deployment/spec.md](./specs/zitadel-self-hosted-deployment/spec.md) was **NOT synced to main spec** (would have propagated the now-rejected prod-specific requirements). The unified-class requirements live in `refactor-unify-env-dispatch`'s spec delta instead.
