# WebAuthn Go Server Libraries Research

> Researched: 2026-02-20

## Summary

`go-webauthn/webauthn` is the unambiguous choice. It is the community-maintained successor to the
deprecated `duo-labs/webauthn`, the only Go library listed on passkeys.dev, and the only one with
documented FIDO2 conformance testing.

## Libraries

### 1. go-webauthn/webauthn — RECOMMENDED

| Field | Value |
|---|---|
| Latest version | v0.15.0 (November 9, 2025) |
| Imported by | 312+ Go projects (pkg.go.dev) |
| Production users | Gitea, Forgejo |
| Listed on passkeys.dev | Yes (only Go library listed) |

**Release history (recent)**:
- v0.15.0 (Nov 2025): Replace `mitchellh/mapstructure` with `go-viper/mapstructure/v2`
- v0.14.0 (Sep 2025): MDS schema 3.1, attestation updates, native app origin validation
- v0.13.0 (May 2025): CaBLE transport, algorithm parameter verification at registration
- v0.12.x: Strict BE/BS flag validation (passkey vs device-bound), WebAuthn Level 3 Credential Record model

**Passkey / Discoverable Credential support**: Full. `requireResidentKey`, `residentKey` preference,
Backup Eligible/Backup State flags. Aligned with Apple/Google/Microsoft passkey behavior.

**Attestation formats verified**: `packed`, `tpm`, `android-key`, `android-safetynet`, `fido-u2f`,
`apple`, `none`. MDS3 integration for AAGUID-based trust.

**Challenge management**: Returns `SessionData` from `BeginRegistration`/`BeginLogin`. Caller is
responsible for storing between Begin and Finish (Redis, HTTP session, encrypted cookie, etc.).

**Limitations**:
- Pre-v1.0: Breaking changes possible between minor versions. Pin to specific minor version.
  A large pre-v1 API consolidation is planned (Discussion #218).
- No built-in HTTP handlers (wire into Connect RPC / HTTP mux manually)
- No built-in session storage

---

### 2. duo-labs/webauthn — DEPRECATED

Last release: December 2022. README explicitly marks it deprecated and links to `go-webauthn/webauthn`.
Do not use for new projects.

---

### 3. Other Libraries — NOT RECOMMENDED

| Library | Reason |
|---|---|
| `pomerium/webauthn` | Internal library for Pomerium proxy; not designed for general passkey flows |
| `egregors/passkey` | Higher-level wrapper over `go-webauthn/webauthn`; adds HTTP scaffolding but no new protocol capability |
| `spiretechnology/go-webauthn` | Low adoption, less active than go-webauthn |
| `e3b0c442/warp` | Not actively maintained through 2024-2025 |

---

## Decision

**Use `go-webauthn/webauthn` v0.15.0.** Pin to this version; review breaking changes documentation
before upgrading across minor versions.

## Sources

- [go-webauthn/webauthn GitHub](https://github.com/go-webauthn/webauthn)
- [go-webauthn/webauthn releases](https://github.com/go-webauthn/webauthn/releases)
- [duo-labs/webauthn GitHub](https://github.com/duo-labs/webauthn)
- [Libraries - passkeys.dev](https://passkeys.dev/docs/tools-libraries/libraries/)
- [Corbado WebAuthn server comparison](https://www.corbado.com/blog/webauthn-server-implementation)
- [go-webauthn pre-v1 API consolidation (Discussion #218)](https://github.com/go-webauthn/webauthn/discussions/218)
