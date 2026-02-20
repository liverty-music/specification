# Frontend WebAuthn + PWA Service Worker Libraries Research

> Researched: 2026-02-20

## Area 1: WebAuthn Client-Side Libraries

### 1. @simplewebauthn/browser — RECOMMENDED

| Field | Value |
|---|---|
| Latest version | 13.2.2 (~October 2025) |
| Weekly npm downloads | ~330,000+ |
| TypeScript | 100% TS; all internal types exported |
| Distribution | npm + JSR |

**Key features for this project**:
- `startAuthentication({ useBrowserAutofill: true })`: Conditional UI / passkey autofill popup
- `startRegistration({ useAutoRegister: true })`: Promote credential to passkey after auth (v11+)
- `preferredAuthenticatorType`: `'localDevice' | 'securityKey' | 'remoteDevice'` hint (v13)
- Framework-agnostic: plain async functions, works cleanly in Aurelia 2

**Breaking changes from older versions**: "attestation/assertion" renamed to "registration/authentication".
In v13, `@simplewebauthn/types` was folded into `browser` and `server` packages directly.

**v13.2.2 security**: Added supply-chain transparency via hardened GitHub Actions CI workflows.

---

### 2. @github/webauthn-json — ARCHIVED, DO NOT USE

**Archived: August 26, 2025 (read-only)**

Reason: All major browsers now ship native JSON parsing for WebAuthn:
- `PublicKeyCredential.parseCreationOptionsFromJSON()`
- `PublicKeyCredential.parseRequestOptionsFromJSON()`

The library's sole purpose (base64url encoding/decoding) is now a browser built-in. The GitHub
team explicitly recommends migrating to `@simplewebauthn/browser` or using the raw API with
native JSON helpers.

---

### 3. @passwordless-id/webauthn — NICHE ALTERNATIVE

| Field | Value |
|---|---|
| Version | ~2.x (last published March 2025) |
| Weekly downloads | ~22,000 |

Unified client+server package, zero dependencies. Missing: conditional UI, auto-register passkey,
authenticator type hints. Slower update cadence than SimpleWebAuthn. Acceptable for simple cases
but weaker for production passkey flows.

---

### 4. Raw navigator.credentials API

**When to use directly**:
- Need cutting-edge extensions (`prf`, `largeBlob`, `signal` API) not yet wrapped by libraries
- Zero-dependency/compliance requirement
- Already on browsers with native JSON helpers (available from Chrome 108+, Firefox 122+)

**Not recommended for production passkey flows**: ArrayBuffer serialization, CBOR/COSE structures,
and conditional UI `AbortController` logic are error-prone to implement manually. Google's own
passkey documentation recommends using a library.

---

## Area 2: PWA Service Worker Management

### 1. Workbox 7.4.0 — FOUNDATION

| Field | Value |
|---|---|
| Latest version | 7.4.0 (~November 2025) |
| Owner | Chrome's Aurora team |
| TypeScript | Full (rewritten in TS at v6.5.0) |

**Relevant modules**:

| Module | Purpose |
|---|---|
| `workbox-precaching` | Precache app shell JS/CSS at install |
| `workbox-strategies` | Runtime caching strategies (CacheFirst, NetworkFirst, StaleWhileRevalidate) |
| `workbox-routing` | Route fetch events to strategies |
| `workbox-expiration` | Evict cached entries by age or count |
| `workbox-range-requests` | Handle `Range:` headers for large binary streaming |

**Critical constraint for ZK circuit files**:

Default `maximumFileSizeToCacheInBytes` = **2 MiB**. Circuit `.zkey` files are 5–30 MB — this
limit must be raised in config, or use runtime caching instead of precaching.

From `vite-plugin-pwa` v0.20.2+: build error thrown if any file exceeds the limit without explicit
config override.

**Browser Cache Storage quota**: Chrome allows up to 80% of disk. Mobile Safari is more conservative.
5–30 MB per circuit version is within quota but should be monitored.

---

### 2. vite-plugin-pwa 1.2.0 — USE WITH injectManifest MODE

| Field | Value |
|---|---|
| Latest version | 1.2.0 (~November 2025) |
| Workbox bundled | Workbox 7.x |

**Two modes**:

| Mode | When to use |
|---|---|
| `generateSW` | Standard app shell + API caching; zero custom SW code |
| `injectManifest` | Custom SW logic required (ZK circuit routing) — **USE THIS** |

The `injectManifest` mode builds a custom `sw.ts` and injects the precache manifest. Required for
ZK circuit caching because the custom `registerRoute` logic cannot be expressed in `generateSW`'s
declarative config.

**Recommended custom SW pattern for ZK circuits**:

```ts
// sw.ts
import { precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { CacheFirst } from 'workbox-strategies'
import { CacheableResponsePlugin } from 'workbox-cacheable-response'
import { ExpirationPlugin } from 'workbox-expiration'

// Standard app shell (injected by vite-plugin-pwa)
precacheAndRoute(self.__WB_MANIFEST)

// Runtime cache for ZK circuit files (versioned CDN URLs)
registerRoute(
  ({ url }) => url.pathname.endsWith('.wasm') || url.pathname.endsWith('.zkey'),
  new CacheFirst({
    cacheName: 'zk-circuits-v1',
    plugins: [
      new CacheableResponsePlugin({ statuses: [200] }),
      new ExpirationPlugin({
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
      }),
    ],
  }),
)
```

Cache invalidation: deploy new versioned URL (e.g., `/circuits/ticketcheck-v2.zkey`) → old cache
evicted on SW activation.

**vite.config.ts**:
```ts
VitePWA({
  strategies: 'injectManifest',
  srcDir: 'src',
  filename: 'sw.ts',
  workbox: {
    maximumFileSizeToCacheInBytes: 60 * 1024 * 1024, // 60 MB
  },
})
```

---

### 3. sw-precache / sw-toolbox — ARCHIVED, DO NOT USE

Both archived under `GoogleChromeLabs`. Migration guide at
developer.chrome.com/docs/workbox/migration/migrate-from-sw/.

---

### 4. Manual Service Worker (OPFS) — Future Option

If `.zkey` files grow beyond ~20 MB, consider Origin Private File System (OPFS):
- Available in all major browsers as of 2025
- Sync file access from workers; quota-exempt on most browsers
- Store large blobs in OPFS from a dedicated Worker; serve from OPFS on fetch
- Workbox has no built-in OPFS support → requires manual SW code for this path

Not required for MVP but document as an upgrade path.

---

## Summary Tables

### WebAuthn Libraries

| Library | Version | Status | Passkey/Conditional UI | Recommendation |
|---|---|---|---|---|
| `@simplewebauthn/browser` | 13.2.2 | Active | Full | **Use** |
| `@github/webauthn-json` | — | Archived Aug 2025 | Never added | Do not use |
| `@passwordless-id/webauthn` | 2.x | Slow cadence | Not highlighted | Niche alternative |

### PWA Libraries

| Library | Version | Status | Large File Support | Recommendation |
|---|---|---|---|---|
| `workbox` | 7.4.0 | Active | Yes (with config) | **Foundation** |
| `vite-plugin-pwa` | 1.2.0 | Active | Yes (injectManifest) | **Use (injectManifest mode)** |
| `sw-precache` / `sw-toolbox` | — | Archived | N/A | Do not use |

## Sources

- [@simplewebauthn/browser docs](https://simplewebauthn.dev/docs/packages/browser/)
- [SimpleWebAuthn GitHub releases](https://github.com/MasterKale/SimpleWebAuthn/releases)
- [@github/webauthn-json GitHub (archived)](https://github.com/github/webauthn-json)
- [Libraries - passkeys.dev](https://passkeys.dev/docs/tools-libraries/libraries/)
- [Workbox - Chrome for Developers](https://developer.chrome.com/docs/workbox)
- [Understanding storage quota - Workbox](https://developer.chrome.com/docs/workbox/understanding-storage-quota)
- [vite-plugin-pwa](https://vite-pwa-org.netlify.app/)
- [vite-plugin-pwa injectManifest docs](https://vite-pwa-org.netlify.app/guide/inject-manifest)
- [Offline-first frontend apps 2025 - LogRocket](https://blog.logrocket.com/offline-first-frontend-apps-2025-indexeddb-sqlite/)
