# Library Research — implement-ticket-system-mvp

> Researched: 2026-02-20
> Purpose: Evaluate all planned libraries/SDKs; confirm decisions reflected in `design.md`

## Files

| File | Domain | Decision |
|---|---|---|
| [zkp-go-backend.md](zkp-go-backend.md) | Go ZKP verification (Groth16) | `gnark` v0.14.0 + `vocdoni/circom2gnark` adapter |
| [zkp-browser-client.md](zkp-browser-client.md) | Browser ZKP proof generation | `circom` + `snarkjs` 0.7.5 (only option) |
| [webauthn-go-server.md](webauthn-go-server.md) | Go WebAuthn/FIDO2 server | `go-webauthn/webauthn` v0.15.0 |
| [evm-aa-go-libraries.md](evm-aa-go-libraries.md) | EVM + ERC-4337 Account Abstraction | `go-ethereum` + raw `net/http` (no AA SDK; all dead) |
| [frontend-webauthn-pwa.md](frontend-webauthn-pwa.md) | Frontend WebAuthn + Service Worker | `@simplewebauthn/browser` v13.2.2; `vite-plugin-pwa` v1.2.0 (injectManifest) |

## Key Findings

### Confirmed (no change needed)
- `circom` + `snarkjs`: Only production-ready Groth16 browser prover; no viable alternative
- `go-webauthn/webauthn`: Only actively maintained Go FIDO2 library
- `@simplewebauthn/browser`: De-facto standard; `@github/webauthn-json` archived Aug 2025
- `vite-plugin-pwa` + Workbox: Confirmed stack; requires `injectManifest` mode for ZK circuits

### Changed from original design assumptions
- **gnark requires adapter**: `vocdoni/circom2gnark` is mandatory — gnark does not natively parse snarkjs JSON
- **Go AA SDK dead**: stackup-go (archived Oct 2024), thirdweb Go SDK (archived May 2024), no Safe Go SDK → implement UserOperation manually with `go-ethereum` + `net/http`
- **Service Worker caching**: `.zkey` files (5–30 MB) exceed Workbox's 2 MB precache limit → use runtime CacheFirst strategy with versioned CDN URLs
- **@github/webauthn-json removed**: Archived Aug 2025; browsers have native JSON parsing

### Monitoring
- `mopro` issue #290 (wasm-bindgen browser): If this lands in 2026, could replace snarkjs with 10–20x faster proving
- `gnark` issue #1582: Native snarkjs JSON export; would eliminate circom2gnark dependency if merged
- `go-webauthn/webauthn` pre-v1 API consolidation (Discussion #218): Review before upgrading
