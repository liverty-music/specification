## Context

The platform stores two Zitadel `MachineUser` JWT private keys in GCP Secret Manager (GSM):

- **`zitadel-admin-sa-key`** — written by an in-pod `bootstrap-uploader` sidecar on first Zitadel boot; read by Pulumi at apply time to authenticate the `@pulumiverse/zitadel` provider as the `pulumi-admin` MachineUser.
- **`zitadel-machine-key`** — written by Pulumi as the `keyDetails` output of a `zitadel.MachineKey` resource; mirrored into a K8s `Secret` via ESO `ExternalSecret`; mounted as a file into backend `server` + `consumer` pods; read by the backend Go service to authenticate as the `backend-app` MachineUser when calling Zitadel Management APIs.

The two names follow inconsistent conventions, neither encoding the binding between the GSM secret and the owning Zitadel principal. The §13.15 incident chain (`fix(zitadel): refresh backend-app MachineKey to align with self-hosted`) traced part of its triage cost to this ambiguity.

The `self-hosted-zitadel` change was archived on 2026-05-11, so the spec target — `openspec/specs/zitadel-self-hosted-deployment/spec.md`, where the "Backend MachineKey Lifecycle Tied to Zitadel-Side Identity" requirement now lives — is stable and available for a `MODIFIED Requirements` delta.

## Goals / Non-Goals

**Goals:**

- Apply a single uniform GSM naming convention `zitadel-machine-key-for-<principal>` to all Zitadel `MachineKey` credentials.
- Achieve **zero downtime** for backend during the rename.
- Keep every step **reversible by a single revert** until the destroy step.
- Allow the backend-app migration and the pulumi-admin migration to **run independently in parallel**.
- Restore symmetry between admin and backend credential names.

**Non-Goals:**

- Renaming Pulumi resource ids (`backend-app`, `backend-app-key`, `pulumi-admin`). They match Zitadel `userName` and are internal to Pulumi state; renaming forces a state-replace cycle with no operator-facing benefit and a real risk of re-minting the MachineKey.
- Renaming the K8s ServiceAccount `backend-app` to disambiguate the three-system `backend-app` overload. This is a separate architectural decision (would touch every backend deployment manifest + Workload Identity binding).
- Tight coordination with `k8s-naming-cleanup` beyond a shared maintenance window. Disjoint files, different risk profiles.

## Decisions

### D1 — Naming pattern: `zitadel-machine-key-for-<principal>`

**Chosen:** `zitadel-machine-key-for-backend-app`, `zitadel-machine-key-for-pulumi-admin`.

**Rationale:**
- `machine-key` mirrors the Zitadel/Pulumi resource type (`zitadel.MachineKey`); a reader cross-referencing Zitadel docs finds the term verbatim.
- `for-<principal>` makes binding direction explicit. The preposition signals "the suffix is the *owning principal*, not the *consuming system*" — resolving the `backend-app` overload (K8s SA, GCP IAM SA, Zitadel MachineUser all share the name).
- Restores symmetry: both keys now follow the same shape.
- Extends naturally: any future MachineUser becomes `zitadel-machine-key-for-<new-principal>`.

**Alternatives considered:**

| Option | Why rejected |
|---|---|
| `zitadel-backend-app-key` (v1 proposal) | `backend-app` overload — reader cannot tell which ID system's credential is stored. |
| `zitadel-backend-app-sa-key` | `-sa-` placement ambiguous; reads as `backend-app-sa` (one token) or `backend-app + sa-key` (two tokens). |
| `zitadel-backend-app-machine-key` | Functional but breaks symmetry with `zitadel-admin-sa-key`'s positioning of the type marker. |
| `zitadel-sa-<principal>-key` | Forces simultaneous rename of `zitadel-admin-sa-key` to maintain symmetry, but no clearer than the chosen pattern. |

### D2 — Asymmetric migration shapes: 6 steps for backend-app, 3 steps for pulumi-admin

**Chosen:** Tailor each migration to its consumer profile rather than forcing a uniform plan.

| | backend-app key | pulumi-admin key |
|---|---|---|
| Writer | Pulumi (every apply) | `bootstrap-uploader` sidecar (every Zitadel pod start, idempotent) |
| Reader | Backend Go pods (continuous) via ESO → K8s Secret → mounted file | Pulumi only (apply time) |
| ESO involved | Yes | No |
| Pod restart needed for cutover | Yes (Reloader-driven on K8s Secret change) | No |
| Soak period before destroy | 7 days (operator confidence in stable read of new) | 1 successful Pulumi apply cycle |
| Min steps for zero downtime | 6 | 3 |

**Rationale:** Imposing 6 steps on the admin migration wastes effort with no risk reduction (no running consumer to break). Imposing 3 steps on the backend migration would skip the env-var transition and force backend to atomically swap the file it reads, eliminating the rollback granularity that motivates the split.

### D3 — Env var name tracks the GSM secret name

**Chosen:** `ZITADEL_MACHINE_KEY_PATH` → `ZITADEL_MACHINE_KEY_FOR_BACKEND_APP_PATH`. Go field renamed to match.

**Rationale:** Preserve a 1:1 mental model: `GSM secret name → ExternalSecret remoteRef.key → ExternalSecret secretKey → mounted file basename → env var → Go field`. A reader navigating any layer arrives at the same name.

**Cost:** Adds one step to the migration (backend must accept new env var while old still set, then drop old) — bringing the total from 5 to 6.

**Alternatives considered:**
- Keep `ZITADEL_MACHINE_KEY_PATH` unchanged, only swap the file basename it points at → 5 steps, backend ships no code change, but leaves long-term inconsistency between env var name and the resource it references. Rejected because the rename's goal is to *eliminate* that kind of ambiguity, not localize it.
- Rebrand env var by purpose (`ZITADEL_API_KEY_PATH`) → loses the 1:1 correspondence, decouples future debugging where an operator greps for the GSM secret name.

### D4 — Pulumi MachineKey URN aligned via `aliases` (state-replace avoided)

**Chosen:** Rename `zitadel.MachineKey('backend-app-key', ...)` → `zitadel.MachineKey('machine-key-for-backend-app', ...)`, attached with `aliases: [{ name: 'backend-app-key' }]` so Pulumi treats the new URN as the same resource. **MachineUser URNs (`backend-app`, `pulumi-admin`) remain unchanged** — they already match Zitadel `userName` 1:1 and reshaping them would break that correspondence.

**Rationale:**
- Pulumi's `aliases` mechanism maps the old URN onto the new URN at plan time, so no `create-replace-delete` cycle occurs. The §13.15 failure mode (MachineKey re-mint → `Errors.AuthNKey.NotFound`) is impossible here because the underlying provider resource is not replaced — only the Pulumi-side URN is updated.
- Closes the last naming inconsistency. After this change, the GSM secret name, the Pulumi MachineKey URN, the K8s file path, the env var, and the Go field all share the `for-<principal>` shape.
- Symmetric with the rest of the change: choosing "completely consistent" over "mostly consistent" was the rule for both the env var rename (D3) and the spec target (D5).

**Alternatives considered:**

| Option | Why rejected |
|---|---|
| Leave Pulumi URN unchanged | Asymmetric — only the Pulumi-side URN keeps the old name, contradicting "complete naming consistency". |
| `pulumi state rename` (manual CLI) | Escape-hatch, not declarative, no PR review. Reserve for state-recovery scenarios per `docs/runbooks/pulumi-state-recovery.md`. |
| Skip aliases, accept state-replace | Forces `create-replace-delete` on the `MachineKey` — the exact failure mode §13.15 produced. Hard no. |
| Also rename MachineUser URNs to `machine-user-for-<principal>` | Breaks 1:1 correspondence with Zitadel `userName`. The MachineUser URN is the principal's identifier, not a credential descriptor. |

**Cleanup:** The `aliases` line is operationally dead once Pulumi has applied the renamed URN. A follow-up PR removes it after a ≥ 14-day soak. The soak is longer than the GSM destroy soak (7 days) because alias removal has no rollback urgency — the alias just sits there until removed.

### D5 — Spec deltas against two landed specs

**Chosen:** Author deltas against **both** landed specs that reference the legacy GSM secret names:

- `openspec/specs/zitadel-self-hosted-deployment/spec.md` — `MODIFIED` for "Bootstrap Admin Machine Key Stored in Secret Manager" and "Backend MachineKey Lifecycle Tied to Zitadel-Side Identity"; `ADDED` for "GSM Naming Convention for Zitadel MachineKey Credentials" (codifies the `zitadel-machine-key-for-<principal>` pattern as a normative convention).
- `openspec/specs/identity-management/spec.md` — `MODIFIED` for "Retain Break-glass Machine User" (4 references to `zitadel-admin-sa-key` in body + 2 scenarios).

**Rationale:** `self-hosted-zitadel` archived on 2026-05-11, so both target specs exist in `specs/`. The lifecycle / bootstrap / break-glass semantics are all unchanged; only the GSM secret names change. The ADDED requirement is what prevents the convention itself from being forgotten — without it, future MachineUsers might invent yet another naming scheme and recreate the inconsistency this change is removing.

**Discovery note:** The `identity-management` delta was identified during pre-flight (1.2) as a gap; an initial scoping only listed `zitadel-self-hosted-deployment`. The pre-flight grep across the four repos surfaced 4 additional references in `Requirement: Retain Break-glass Machine User`, prompting expansion.

## Risks / Trade-offs

**[R1] ESO refresh lag during step 3 transition** — When Pulumi adds the new GSM secret and the `ExternalSecret` is updated to read both, ESO's `refreshInterval` (currently 1h) governs how quickly the K8s Secret reflects the new data. → **Mitigation:** soak each transitional step for ≥1 ESO refresh cycle in dev (effectively next-day) before progressing.

**[R2] Backend env-var transition ordering** — If cp step 4 (configmap drops old env var) lands before be step 2 (backend reads new with fallback) is fully deployed, pods restart without the env var they expect. → **Mitigation:** each PR description SHALL declare its predecessor; downstream PRs SHALL NOT merge until the predecessor is **deployed in dev** (not merely merged). Verify via ArgoCD sync status.

**[R3] Destroy step is one-way** — GSM `SecretManagerSecret` destruction releases the resource id; recreating with the same name + version history requires manual Pulumi state import or accepting a fresh history. → **Mitigation:** mandatory 7-day soak for backend-app (covers a weekly on-call rotation); mandatory 1-cycle Pulumi apply confirmation for pulumi-admin.

**[R4] `bootstrap-uploader` dual-write fragility** — During pulumi-admin's step 1, the sidecar writes the same value to two GSM secret names. If write to one fails (network, IAM, etc.), the two could drift. → **Mitigation:** writes are idempotent; failures surface in sidecar logs; the secret payload is byte-identical between names so a partial write does not produce a "two valid but different keys" scenario.

**[R5] Pulumi-admin migration touches `@pulumiverse/zitadel` provider config** — Switching Pulumi to read the new GSM secret means updating the provider's `jwtProfileJson` source. A misconfiguration here breaks the next `pulumi up` (provider auth fails). → **Mitigation:** verify in `pulumi preview` that the provider resolves before merging step 2; the old secret still exists as a fallback for manual rollback.

**[R6] Verbose Go field name** — `ZitadelMachineKeyForBackendAppPath` is 33 chars (vs the prior 21). → **Mitigation:** referenced only at DI wiring (3 sites); not user-facing; readability of `envconfig` tag matters more.

**[R7] `bootstrap-uploader` dual-write does not fire on already-bootstrapped instances** — The sidecar's `while [ ! -f "$KEY_FILE" ]; do sleep 2; done` loop blocks until Zitadel writes the admin key file to the shared `emptyDir`. Per the "Subsequent boots skip bootstrap" scenario in `zitadel-self-hosted-deployment`, that write only happens on first-instance bootstrap against an empty database; subsequent pod restarts leave the sidecar idling forever. → **Consequence:** PR 10's dual-write code path is only exercised on a fresh Zitadel instance. On an already-bootstrapped environment (e.g., dev at the time this change rolls out), the new GSM secret `zitadel-machine-key-for-pulumi-admin` will exist as an empty resource shell with no `SecretVersion`, and PR 11 (Pulumi switches to read the new name) would fail authentication. → **Mitigation:** between PR 10 deploy and PR 11 author/merge, an operator SHALL perform a **one-shot manual seed** of the new secret from the legacy `zitadel-admin-sa-key` value:

```bash
set -euo pipefail
TMP=$(mktemp)
# Guarantee cleanup even on SIGINT / network hang. Without the trap,
# Ctrl+C during a hung `gcloud secrets versions add` leaves the
# admin SA private key sitting unshredded on local disk.
trap 'shred -u "$TMP" 2>/dev/null || rm -f "$TMP"' EXIT
gcloud secrets versions access latest --secret=zitadel-admin-sa-key \
  --project=liverty-music-dev --out-file="$TMP"
gcloud secrets versions add zitadel-machine-key-for-pulumi-admin \
  --project=liverty-music-dev --data-file="$TMP"
shred -u "$TMP"
```

The seed is byte-identical to the legacy secret, so once `bootstrap-uploader` does eventually fire (next first-instance bootstrap), its idempotency check (`if [ "$existing" = "$(cat "$KEY_FILE")" ]; then ... skipping upload`) treats the seeded value as already-current and does NOT overwrite. **Spec invariant note:** the documented invariant "only legitimate write to admin-sa-key SHALL be performed by `bootstrap-uploader`" is preserved in spirit — the seeded value is byte-equal to the value `bootstrap-uploader` would have written — but the writer of record for this one-time copy is the operator, not the sidecar. The transition completes the moment PR 12 destroys the legacy resource.

## Migration Plan

### backend-app key — 6-step zero-downtime split

```
S0:  GSM=old / ESO=old / Pod mount=old file / Env=OLD only
  │ Step 1 (cp): Pulumi adds new GSM SecretManagerSecret + SecretVersion
  │              populated from the same MachineKey.keyDetails output
  ▼
S1:  GSM=old+new / ESO=old / Pod mount=old / Env=OLD
  │ Step 2 (be): Backend Config accepts NEW env var; reads NEW with
  │              fallback to OLD. Ship as code-only PR (env not yet set).
  ▼
S2:  Backend reads NEW||OLD via Go fallback
  │ Step 3 (cp): ExternalSecret adds new entry; deployment mounts new file
  │              alongside old; configmap exports NEW env var pointing at
  │              new path (OLD env var retained). Reloader triggers pod
  │              restart; pods now read NEW file via the new env var.
  ▼
S3:  ESO=old+new / Pod mount=old+new / Env=NEW (OLD set but unused by Go fallback)
  │ Step 4 (cp): Pulumi removes old GSM writer; ExternalSecret + configmap
  │              + deployment drop OLD entries. Reloader restart picks up
  │              the trimmed Secret.
  ▼
S4:  ESO=new only / Pod mount=new only / Env=NEW (≥ 7-day soak begins)
  │ Step 5 (be): Backend Config drops OLD env var field + fallback branch.
  │              Code-only PR; effectively dead-code removal.
  ▼
S5:  Backend reads NEW only (Go field collapsed)
  │ Step 6 (cp): Destroy old GSM SecretManagerSecret resource.
  ▼
S6:  Complete
```

### backend-app MachineKey Pulumi URN rename (PRs 7–8)

Independent of the GSM rename arc above. The two PRs MAY interleave with, or run after, the GSM rename steps — they do not gate any GSM step.

```
U0:  Pulumi MachineKey URN = 'backend-app-key'
  │ PR 7 (cp): Rename URN to 'machine-key-for-backend-app';
  │            attach aliases: [{ name: 'backend-app-key' }].
  │            pulumi preview SHALL show URN update only,
  │            NO replacement, NO key re-mint.
  ▼
U1:  Pulumi state keyed on new URN; alias still present
  │ ─── ≥ 14-day soak ───
  │ PR 8 (cp): Remove the aliases line.
  ▼
U2:  Code-state alignment complete; alias-as-dead-code removed
```

### pulumi-admin key — 3-step migration

```
T0:  GSM=old / bootstrap-uploader writes old / Pulumi provider reads old
  │ Step 1 (cp): bootstrap-uploader writes both old + new GSM secrets
  │              from the same admin SA key payload.
  ▼
T1:  GSM=old+new / both writes succeed on next Zitadel pod boot
  │ Step 2 (cp): Pulumi provider config switches to read the new GSM
  │              secret. Verify pulumi preview resolves before merge.
  ▼
T2:  Pulumi reads new / bootstrap-uploader continues dual-write
  │ Step 3 (cp): bootstrap-uploader drops the old write; destroy the
  │              old GSM SecretManagerSecret.
  ▼
T3:  Complete
```

### Ordering and parallelism

- The backend-app and pulumi-admin migrations are independent. They MAY run concurrently. Recommended: start both at the same maintenance window so a single "Zitadel credentials cleanup" arc completes together.
- Within each migration, steps SHALL be sequential and each PR declares its predecessor by URL in the description.

### Rollback strategy

- **Pre-destroy (steps 1–5 / 1–2):** Revert the most recent PR; the prior state resumes once ArgoCD/Pulumi reconcile.
- **Post-destroy (step 6 / 3):** Re-add the old GSM `SecretManagerSecret` resource in Pulumi (the underlying `MachineKey.keyDetails` output still exists in Pulumi state). The secret history is lost but the current value is restored.

## Open Questions

None blocking. The proposal's prior Option A/B question on spec delta location is resolved (Option B selected because `self-hosted-zitadel` archived on 2026-05-11).
