## Context

The consumer SPA (`frontend` repo) is an Aurelia 2 app built with Vite, served by
Caddy from a single container image, authenticated against Zitadel via
`oidc-client-ts` (PKCE), and configured at runtime by fetching `/config.json`
(mounted per-environment as a Kubernetes ConfigMap). Zitadel is split into two
orgs:

- **`admin` role org** — internal humans, **Google Workspace IDP** already wired
  (`google-admin-idp`, per archived change `add-zitadel-console-admin-via-google-idp`).
- **`liverty-music` product org** — end-user fans, passkey-only login policy.

There is no internal developer/operator web UI. This design establishes the
foundation for one at `admin.liverty-music.app`. Features are out of scope and
ship in later changes; this change delivers auth + an empty authenticated shell.

Key existing invariants this design must respect:

- `loadAppConfig()` fetches `/config.json` from a **hardcoded path**; the whole
  codebase assumes **one app → one `/config.json`** (also enforced by
  `KNOWN_HOSTS` / `validateEnvironmentMatchesHost`).
- The consumer image's `Caddyfile` SPA-fallback is `try_files {path} /index.html`.
- Delivery is GitOps: image → Artifact Registry → ArgoCD image-updater (digest) →
  ArgoCD sync. Prod is a heavier GH-Release-driven retag + pin-bump path.

## Goals / Non-Goals

**Goals:**

- A deployed, access-controlled `admin.liverty-music.app` that only internal
  Google Workspace accounts can sign into, showing a welcome placeholder.
- **Zero impact** on the consumer SPA's bundle size, Core Web Vitals, hosting,
  Zitadel app, or release cadence.
- Maximum reuse of existing patterns (auth-service, runtime-config contract,
  gateway, ArgoCD) with a clean seam for future extraction to its own repo.

**Non-Goals:**

- Any admin feature, RPC, or backend endpoint.
- Authorization granularity beyond the Google-IDP authentication gate (no admin
  roles/scopes yet).
- Audit logging, session policy hardening, or admin-specific observability.
- Migrating or changing the consumer SPA in any behavioral way.

## Decisions

### D1 — Auth via the `admin` org + Google Workspace IDP (authN as the boundary)

The admin console authenticates against the **`admin` org**, reusing
`oidc-client-ts` PKCE exactly like the consumer SPA, but passing the admin org id
in the `urn:zitadel:iam:org:id:<id>` scope so Zitadel applies the admin org's
Google-IDP login policy. Because only Google Workspace accounts can complete that
flow, **authentication itself is the access boundary** — no separate
authorization layer is needed for the foundation.

- *Why over reusing the product org (passkey) + a role check (authZ boundary)?*
  Every fan can already authenticate against the product org, so that path would
  require building and maintaining a role/claim gate just to keep fans out. The
  admin org gives the boundary for free and matches the "developer-only" intent.
  Confirmed acceptable: all current admin users have Google Workspace accounts.
- *Future:* if non-Workspace operators ever need access, add Zitadel project
  roles + an ID-token role guard then (the consumer app already enables
  `idTokenRoleAssertion`).

A new `ApplicationOidc` is provisioned **in the admin org** (SPA / PKCE / no
secret), with redirect URIs `https://admin.{dev,}liverty-music.app/auth/callback`
and matching post-logout URIs. It is a sibling of the consumer `web-frontend`
app, not a modification of it.

### D2 — One repo, two Vite entry points (MPA), bundle-isolated

The admin app lives in the **same `frontend` repo** as a **second Vite/Rollup
HTML entry** (`admin.html` → admin bootstrap). Rollup builds an independent chunk
graph per entry, so consumer pages load only consumer chunks; admin-only code is
never shipped to fans. Shared modules (e.g. `AuthService`, the config loader)
become shared chunks only when both entries import them — which the consumer
already loads, so its bundle does not grow.

- *Why over Aurelia runtime "multi-root"?* Multi-root (`new Aurelia()` ×N on one
  page) is a runtime composition feature; both roots ship in **one bundle**, so
  it does **not** isolate bundles. It solves a different problem (multiple mount
  points on a single page) and would defeat the zero-impact goal.
- *Why over a separate repo now?* A placeholder does not justify standing up a
  whole new repo + CI + visual-baseline pipeline + ArgoCD app from scratch.
  One-repo MPA reuses tooling; D4 keeps a clean extraction seam for later.

### D3 — Dedicated top-level `frontend/admin/` directory (not `src/admin/`)

Admin source lives in a top-level `admin/` directory, sibling to `src/`, with
cross-app code in a shared location both can import:

```
frontend/
  index.html              # consumer entry (unchanged)
  admin.html              # admin entry (new)
  src/                    # consumer app (unchanged)
  admin/                  # admin app (new, self-contained)
    main.ts               # admin bootstrap (reuses shared AuthService, admin org id)
    admin-shell.ts/.html  # welcome placeholder shell + route guard
  shared/                 # the ONLY cross-app import surface
    services/auth-service.ts
    config/app-config.ts
```

- *Why over `src/admin/`?* A top-level directory makes the boundary **physical**:
  the seam between "consumer", "admin", and "shared" is visible in the tree and
  trivial to enforce with an import-boundary lint rule (admin and src may only
  cross via `shared/`). It also mirrors ③b's runtime isolation at the source
  level and means a future extraction is "lift `admin/` + `shared/` into a new
  repo" rather than untangling intertwined `src/` subtrees.
- *Trade-off:* tsconfig / Vite / Biome / Vitest must be made aware of the extra
  root. This is config-only and one-time.

### D4 — Separate image + separate Deployment for serving (option ③b)

The admin console is served by its **own container image** (admin `Dockerfile` +
`Caddyfile`) and its **own Kubernetes Deployment/Service/HTTPRoute**, behind the
same shared external gateway, rather than co-served from the consumer pod by
Host-based Caddy routing (③a).

- *Why over ③a (same image, host-routed Caddy)?* ③a has fewer k8s objects but
  forces two **load-bearing** seams to become host-conditional, breaking
  codebase invariants:
  1. **config delivery** — a single pod serving one `/config.json` cannot hand
     the admin entry its different org id/client id without either a host-aware
     Caddy rewrite or parameterizing the hardcoded `loadAppConfig()` path.
  2. **SPA fallback** — `try_files` must branch per host (`/admin.html` vs
     `/index.html`).
  Plus both ConfigMaps would mount on one Deployment, so a Reloader restart from
  an admin config change would **also restart the consumer pod** (blast-radius
  leak), and admin/consumer would deploy in **lockstep** (an admin copy tweak
  would re-release the consumer prod image).
- ③b keeps every invariant intact: the admin pod mounts its **own** `/config.json`
  at the canonical path → `loadAppConfig()` is reused unchanged; the admin
  `Caddyfile` is a trivial single-fallback copy; ConfigMap blast radius and
  release cadence are isolated. Cost is **+1 small pod** (dev spot, negligible)
  and a set of **clean copies** of existing k8s/Pulumi patterns.
- *Build vs serve split:* `npm run build` stays **one build** producing both
  entries into `dist/`; only the serving layer (Dockerfile/Caddyfile) is split
  into a second image. The admin image copies/serves the admin entry's output.

### D5 — Reuse the existing GitOps delivery path

The admin image is published to Artifact Registry and tracked by the existing
ArgoCD **image-updater** as its own alias, synced by ArgoCD like the consumer
app. Admin and consumer are independent artifacts and release independently
(direct consequence of D4).

## Risks / Trade-offs

- **Import boundary erosion** (a `src/` ↔ `admin/` import sneaks in, leaking
  admin code into the consumer bundle) → Add a dependency/import-boundary lint
  rule (e.g. Biome `noRestrictedImports` or a dependency-cruiser check) wired
  into `make lint`/CI so a cross-import fails the build. Verify post-build that
  the consumer entry's chunk graph contains no admin modules.
- **PWA service worker over-precaching** — the consumer uses
  `VitePWA injectManifest` (single SW). An MPA build could pull admin assets into
  the precache manifest, or the admin host could register the consumer SW →
  Scope the SW to the consumer entry only; the admin placeholder ships **no SW**.
- **Zitadel admin-org app misconfig** (wrong redirect URI / org scope → login
  loop) → Mirror the consumer app's proven `ApplicationOidc` settings; verify the
  end-to-end Google sign-in on dev before prod.
- **Cert/DNS propagation lag** for the new `admin.*` hostname → Add the hostname
  to certmap + Cloud DNS first; gate the HTTPRoute cutover on cert readiness.
- **Two release paths to remember** — admin now has its own image/release →
  Document the admin release path alongside the consumer's; keep them structurally
  identical to minimize cognitive load.

## Migration Plan

Greenfield surface (no existing admin users/data), so no data migration. Rollout
order, parallelizing per the cross-repo release protocol:

1. **specification**: this change merged → spec is canonical.
2. **cloud-provisioning (Pulumi)**: provision the admin-org `ApplicationOidc`,
   certmap + Cloud DNS entries for `admin.{dev,}liverty-music.app`.
3. **frontend**: add `admin/` + `shared/`, the second Vite entry, admin
   Dockerfile/Caddyfile, import-boundary lint. Build produces both entries.
   Publish the admin image to AR.
4. **cloud-provisioning (k8s)**: admin Deployment/Service/HTTPRoute + per-env
   `admin-app-runtime-config` ConfigMap; image-updater alias; ArgoCD picks it up.
5. Promote to prod via the standard GH-Release/pin-bump path, then verify in
   prod: Google sign-in works, welcome placeholder renders, a non-Workspace
   account is rejected, consumer surface unchanged. There is **no dev
   environment** to verify against first (it is intentionally shut down for cost
   and not part of this rollout), so prod is the verification surface —
   confidence before prod comes from the local build/bundle-isolation checks,
   unit tests, and the `pulumi preview` diffs rather than a live dev sign-in.

**Rollback:** purely additive — remove/disable the admin HTTPRoute (or scale the
admin Deployment to 0). The consumer surface is untouched at every step.

## Resolved Questions

- **Kubernetes namespace / ArgoCD app → reuse the existing `frontend` namespace
  (N1).** The admin workload is added as an `admin/` sibling to `web/` in the
  `frontend` kustomize tree, served by the existing `frontend` ArgoCD
  Application. *Rationale:* the `frontend` namespace carries no NetworkPolicy /
  RBAC / ResourceQuota today, so a separate namespace would duplicate boilerplate
  (a new ArgoCD Application + overlay tree) without an isolation benefit at the
  policy layer. ③b's isolation that actually matters — separate image, pod,
  `/config.json`, and release artifact — is preserved regardless of namespace.
  *Accepted trade-off:* admin and consumer share one ArgoCD Application sync, so a
  malformed admin manifest can mark the `frontend` app `OutOfSync`/`Degraded`.
  Mitigation: keep admin manifests as a clean copy of the consumer pattern and
  rely on the k8s dry-run gate; promote to a dedicated `admin` namespace + ArgoCD
  app if/when admin needs its own NetworkPolicy, quota, or service account.
- **i18n → English-only for the foundation.** The admin console ships no
  `@aurelia/i18n` machinery; the welcome placeholder is English-only. *Rationale:*
  it is an internal developer tool and i18n would add infrastructure to the admin
  bundle for no benefit. If admin later needs localization, it can pull i18n
  through the `shared/` location (D2/D3) at that point.
