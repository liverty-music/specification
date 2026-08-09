# EVM / ERC-4337 Account Abstraction Go Libraries Research

> Researched: 2026-02-20

## Summary

The Go ERC-4337 library ecosystem is essentially dead. All major Go AA SDKs are either archived or
unmaintained. The pragmatic approach is to implement UserOperation construction manually using
`go-ethereum` ABI encoding and call bundler RPC endpoints directly via `net/http`.

## Area 1: EVM Client Libraries

### go-ethereum — REQUIRED

| Field | Value |
|---|---|
| Latest stable | v1.15.x / v1.17.1 (January 2026, includes CVE-2026-26313/14/15 patches) |
| Import path | `github.com/ethereum/go-ethereum` |
| Base network | Full support (same JSON-RPC API as mainnet) |

**Key packages for this project**:
- `ethclient`: Connect to Base Sepolia, send transactions, call contracts
- `accounts/abi`: ABI encoding/decoding for contract calls and UserOperation callData
- `cmd/abigen`: Generate type-safe Go bindings from ABI JSON (Safe contracts)

**v1.15 notable changes**: New DB schema, Prague fork (EIP-7702), removal of Solidity compilation
from `abigen` (supply ABI JSON from Foundry/Hardhat instead).

---

## Area 2: ERC-4337 Account Abstraction SDKs

### Status: All major Go AA SDKs are dead

| Library | Status |
|---|---|
| `stackup-wallet/stackup-bundler` (Go) | **Archived October 20, 2024** |
| `thirdweb-dev/go-sdk` | **Deprecated May 3, 2024** (archived) |
| `safe-global/safe-core-sdk` | TypeScript only; no official Go version |
| `vikkkko/safe-core-sdk-golang` | Single-developer community fork (Sep 2025); unknown maintenance |
| `anyproto/alchemy-aa-sdk` | Third-party unofficial Go wrapper; scope unclear |
| `mdehoog/go-bundler-client` | Thin utility; depends on archived stackup-bundler types |
| Pimlico Go SDK | Does not exist (TypeScript only) |
| permissionless.js Go port | Does not exist |

---

## Decision: Raw Implementation Approach

Given the above, implement ERC-4337 interaction without a Go AA SDK:

### 1. Safe Address Prediction (CREATE2)

Implement directly in Go using `go-ethereum/crypto`:

```
address = keccak256(0xff ++ SafeProxyFactory ++ salt ++ keccak256(initCode))[12:]
```

- SafeProxyFactory Singleton: `0x914d7Fec6aaC8cd542e72Bca78B30650d45643d7` (all chains incl. Base)
- `initCode` encodes the proxy factory call with: Safe singleton address, owners, threshold,
  `Safe4337Module` as fallback handler
- `saltNonce` must be the same value in prediction and future actual deployment

### 2. UserOperation Construction

Build the `UserOperation` struct manually (well-defined in EIP-4337 v0.7). Use `go-ethereum/accounts/abi`
for `callData` encoding of Safe contract method calls.

Generate type-safe Go bindings for Safe contracts with abigen:
```bash
abigen --abi SafeProxyFactory.json --pkg safe --out safe_proxy_factory.go
abigen --abi Safe4337Module.json --pkg safe --out safe_4337_module.go
```

ABIs sourced from `safe-global/safe-smart-account` repository.

### 3. Bundler Submission

Call Pimlico or Alchemy bundler RPC directly via `net/http`:

```go
// POST to https://api.pimlico.io/v2/{chain}/rpc?apikey={key}
// JSON-RPC method: eth_sendUserOperation
// params: [userOp, entryPointAddress]
```

Standard JSON-RPC; no library needed beyond `net/http` + `encoding/json`.

---

## Testing Requirements

- Unit-test ABI encoding against known-good vectors from the ERC-4337 spec
- Integration-test against a local Bundler (e.g., Rundler) in CI
- Integration-test Safe address prediction against actual Safe deployment on Base Sepolia

---

## Sources

- [go-ethereum releases](https://github.com/ethereum/go-ethereum/releases)
- [thirdweb Go SDK deprecation announcement](https://blog.thirdweb.com/changelog/deprecation-announcement-python-go-sdks/)
- [stackup-bundler (archived)](https://github.com/stackup-wallet/stackup-bundler)
- [Etherspot migration from Stackup](https://medium.com/etherspot/etherspots-assistance-for-developers-during-the-migration-from-stackup-0ff6fbb93734)
- [safe-core-sdk (TypeScript)](https://github.com/safe-global/safe-core-sdk)
- [Safe ERC-4337 docs](https://docs.safe.global/advanced/erc-4337/4337-safe)
- [Pimlico bundler docs](https://docs.pimlico.io/references/bundler/usage)
- [abigen docs](https://geth.ethereum.org/docs/tools/abigen)
- [EIP-4337 spec](https://eips.ethereum.org/EIPS/eip-4337)
