## Why

The team has no internal web surface for developer/operator tooling: every
operational task today is done via raw `kubectl`, `gcloud`, SQL, or the Zitadel
console. As the platform approaches launch we need a dedicated, authenticated
home — `admin.liverty-music.app` — that internal developers can grow tooling on.
This change builds only the *foundation* (auth + an empty authenticated shell);
actual admin features land in separate changes. Establishing the foundation now
lets feature work start against a real, deployed, access-controlled surface
instead of blocking on plumbing.

## What Changes

- Introduce a **second Vite entry point** in the existing `frontend` repo so the
  admin console is built alongside the consumer SPA but **bundle-isolated** —
  Rollup splits per HTML entry, so the consumer app never downloads any admin
  code and its bundle size / Core Web Vitals are unaffected.
- Place admin source under a **dedicated top-level `frontend/admin/` directory**
  (sibling to `src/`), with cross-app code consumed from a shared location. This
  makes the import boundary physical and lint-enforceable, and keeps a clean
  seam for future extraction into its own repository.
- Authenticate the admin console with **Zitadel OIDC via the existing `admin`
  role org + Google Workspace IDP** (the same mechanism the consumer SPA uses —
  `oidc-client-ts` PKCE — but scoped to the admin org). Authentication itself is
  the access boundary: only Google Workspace accounts can sign in. A new
  **`ApplicationOidc`** is provisioned in the admin org with admin-host redirect
  URIs.
- Add an **authenticated route guard** and a **post-login welcome placeholder**
  page. No business features.
- Serve the admin console from a **separate container image and Kubernetes
  Deployment/Service** (option ③b) — *not* host-routed off the consumer pod —
  so the consumer SPA's `/config.json` invariant, Caddy SPA-fallback, blast
  radius, and release cadence stay fully isolated. The admin pod mounts its own
  `/config.json` at the canonical path (admin org id + admin client id).
- Add a dedicated **HTTPRoute hostname** for `admin.{dev,}liverty-music.app` on
  the shared external gateway, plus **certmap and Cloud DNS** entries.
- Wire the admin image into the existing **ArgoCD + image-updater** delivery
  path as its own tracked artifact.

## Capabilities

### New Capabilities

- `admin-console`: the developer admin console frontend foundation — a dedicated
  Vite MPA entry in the `frontend` repo built with bundle isolation from the
  consumer SPA, Zitadel OIDC authentication via the admin org + Google Workspace
  IDP, an authenticated route guard, and a post-login welcome placeholder.
- `admin-console-hosting`: serving and delivery for `admin.liverty-music.app` —
  a separate container image and Kubernetes Deployment/Service, a dedicated
  HTTPRoute hostname on the shared external gateway, certmap + Cloud DNS entries,
  per-host runtime config delivery, and the ArgoCD/image-updater wiring. Also
  covers the new admin-org `ApplicationOidc` Zitadel resource.

### Modified Capabilities

None. The admin console reuses the existing `frontend-runtime-config` `/config.json`
contract, the `authentication` OIDC mechanism, and the `gke-gateway-infrastructure`
gateway unchanged — it adds a parallel surface rather than changing their
requirements.

## Impact

- **frontend repo**: new `admin/` top-level directory, a shared code location,
  a second Vite/Rollup entry (`admin.html`), an admin-specific `Dockerfile` +
  `Caddyfile`, admin bootstrap reusing `AuthService` with the admin org id, an
  import-boundary lint rule. Consumer SPA code is untouched; consumer bundle
  output is unchanged.
- **cloud-provisioning repo**:
  - Pulumi: new `ApplicationOidc` in the admin org (`admin-host/auth/callback`
    redirect URIs); admin hostnames added to certmap + Cloud DNS.
  - k8s: an admin Deployment/Service/HTTPRoute added to the existing `frontend`
    namespace (an `admin/` sibling to `web/`, served by the existing `frontend`
    ArgoCD app) + per-env ConfigMap (`admin-app-runtime-config`) for the admin
    pod; ArgoCD image-updater alias for the new admin image.
- **CI/CD**: a second image build/push in the frontend pipeline; admin and
  consumer release independently.
- **No changes to**: backend, Connect-RPC contracts, database, the consumer SPA
  bundle, consumer hosting, or the existing Zitadel consumer app/login policy.
- **Out of scope**: any admin feature/RPC, admin authorization roles beyond the
  Google-IDP authentication gate, audit logging, and admin-specific backend
  endpoints — all deferred to follow-up changes.
