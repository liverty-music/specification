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
| [zitadel-passkey-rp.md](zitadel-passkey-rp.md) | Zitadel as WebAuthn Relying Party | Zitadel RP viable for MVP (hosted UI); custom UI blocked by Issue #8282 |

## Key Findings

### Used in MVP
- `circom` + `snarkjs`: Only production-ready Groth16 browser prover; no viable alternative
- `vite-plugin-pwa` + Workbox: Confirmed stack; requires `injectManifest` mode for ZK circuits
- `gnark` + `vocdoni/circom2gnark`: gnark does not natively parse snarkjs JSON; adapter is mandatory
- `go-ethereum` + `net/http`: All Go AA SDKs dead (stackup-go, thirdweb); manual UserOperation construction
- **Zitadel as Passkey RP**: Viable for MVP with hosted login UI; custom UI blocked by Issue #8282

### Reserved for Option C migration (not used in MVP)
- `go-webauthn/webauthn` v0.15.0: Only actively maintained Go FIDO2 library; needed if self-hosted RP required
- `@simplewebauthn/browser` v13.2.2: De-facto standard browser WebAuthn library; needed for custom Login UI

### Changed from original design assumptions
- **Zitadel is the WebAuthn RP for MVP**: No self-hosted go-webauthn; Passkey handled by Zitadel hosted UI
- **Safe address from users.id**: Credential public key not exported by Zitadel; derive from internal UUID instead
- **Service Worker caching**: `.zkey` files (5-30 MB) exceed Workbox's 2 MB precache limit → runtime CacheFirst strategy
- **@github/webauthn-json removed**: Archived Aug 2025; browsers have native JSON parsing

### Monitoring
- `mopro` issue #290 (wasm-bindgen browser): If this lands in 2026, could replace snarkjs with 10-20x faster proving
- `gnark` issue #1582: Native snarkjs JSON export; would eliminate circom2gnark dependency if merged
- `go-webauthn/webauthn` pre-v1 API consolidation (Discussion #218): Review before upgrading
- Zitadel Issue #8282 (RPOrigins bug): Blocks custom Login UI on different domain
- Zitadel Discussion #8867: Conditional UI (Passkey autofill) not supported
