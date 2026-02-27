# AI Agent Rules - Liverty Music Specification

**CRITICAL: Before ANY action (create file, run command, write code), check Workspace Structure below to determine the correct repository.**

## Workspace Structure and Responsibilities

```
liverty-music/
├── specification/
│   ├── openspec/changes/ ← Ongoing changes (proposals, designs, specs, tasks)
│   ├── openspec/specs/   ← The latest capability specs
│   └── proto/            ← Protobuf entity / RPC schema (no `buf generate`, use BSR)
├── backend/               ← Go implementation (Connect-RPC services)
├── frontend/              ← Aurelia 2 PWA implementation
└── cloud-provisioning/
    ├── src/               ← Pulumi code (GCP, Cloudflare, GitHub resources)
    └── k8s/               ← Kubernetes manifests (Kustomize base/overlays)
```

## Decision Process (Required Before Action)

**For every file creation, code generation, or command execution:**

1. **Identify the artifact type** (OpenSpec change? Protobuf? Go code? Pulumi? K8s manifest?)
2. **Check Workspace Structure** above to find the correct repository
3. **Verify you're in the correct directory** before proceeding
4. **If uncertain, ask** - never guess the repository location

---

## What This Repository Is

Protocol Buffers schema repository for **Liverty Music** — a personalized concert notification platform. Defines entity and RPC interfaces using Buf, with remote code generation via Buf Schema Registry (BSR). No application code lives here; this repo is the single source of truth for API contracts consumed by the Go backend and TypeScript frontend.

## Essential Commands

```bash
mise install                              # Install toolchain (buf, pre-commit)
pre-commit install                        # Install commit hooks
pre-commit install --hook-type pre-push   # Install push hooks

buf lint                                  # Lint proto files (STANDARD + COMMENTS rules)
buf format -w                             # Auto-format proto files
buf breaking --against '.git#branch=main' # Check for breaking changes
```

Pre-commit hooks run `buf lint`, `buf format -w`, and `buf breaking` automatically on commit. If a breaking change is intentional, add the `buf skip breaking` label to the PR.

## Architecture

### Layered Proto Structure

```
proto/liverty_music/
├── entity/v1/    # Core business entities — the domain model
│   ├── entity.proto   # Package-level doc (no messages)
│   ├── user.proto     # User, UserId, UserEmail
│   ├── artist.proto   # Artist, ArtistId, OfficialSite, Mbid
│   ├── concert.proto  # Concert, ConcertId, ConcertTitle
│   └── venue.proto    # Venue, VenueId, VenueName
└── rpc/          # Service definitions — one service per subdirectory
    ├── user/v1/user_service.proto       # UserService (Get, Create)
    ├── artist/v1/artist_service.proto   # ArtistService (CRUD, Search, Follow, Similar, Top)
    └── concert/v1/concert_service.proto # ConcertService (List, SearchNewConcerts)
```

- **Entity layer** (`entity/v1/`): Pure data types. No service logic. Every domain concept gets a wrapper message (e.g., `UserId` wraps `string` with UUID validation) — never use raw primitives for domain types.
- **RPC layer** (`rpc/*/v1/`): Service definitions that import entity types. Follow Google AIP resource-oriented patterns.

### Key Design Conventions

- **Type-safe IDs**: All identifiers are wrapper messages (`UserId`, `ArtistId`, etc.) with `protovalidate` constraints, not bare `string` fields.
- **Validation**: Uses `buf.validate` (protovalidate) for field-level constraints. All required fields are annotated.
- **Dependencies**: `buf.build/googleapis/googleapis` (field_behavior, common types) and `buf.build/bufbuild/protovalidate`.
- **Buf config**: `buf.yaml` enables `STANDARD` + `COMMENTS` lint rules (except `PACKAGE_SAME_GO_PACKAGE`); breaking change detection uses `FILE` strategy.

### Code Generation

Generated code is hosted on BSR at `buf.build/liverty-music/schema` — **never commit a `gen/` directory**.

**CRITICAL: NEVER run `buf push` locally.** BSR push is performed exclusively by GitHub Actions on release publish (`buf-release.yml`). To publish proto changes to BSR, create a GitHub Release after merging to main. Consumers install generated packages via `go get` or `npm install` from BSR.

## OpenSpec Workflow

This repo uses OpenSpec for structured specification changes. Changes live in `openspec/changes/` and follow an artifact workflow (proposal → design → specs → tasks). Use `/opsx:new` to start a new change and `/opsx:continue` to progress through artifacts. See `.claude/skills/` for full skill documentation.

## Poly-repo Context

- **This repo** (`specification`): Proto schemas, OpenSpec specs, product design docs
- **Backend** (`liverty-music/backend`): Go application
- **Cloud Provisioning** (`liverty-music/cloud-provisioning`): GCP infrastructure

## Forbidden Operations

These commands are **CI-only**. NEVER execute them locally, and NEVER suggest the user run them manually either.

| Command | CI Trigger | Workflow File |
|---------|------------|---------------|
| `buf push` | GitHub Release published | `.github/workflows/buf-release.yml` |
| `buf generate` | Not used — BSR handles remote generation | N/A |

If the user requests BSR publishing or code generation:
1. **REFUSE** local execution
2. **Explain**: BSR push happens automatically when a GitHub Release is published
3. **Guide**: "Create a PR → merge → create Release → CI pushes to BSR"

## Release Process

```
1. Create PR to main     → buf-pr-checks.yml validates (lint, breaking changes)
2. Merge PR to main
3. Create GitHub Release  → tag: vX.Y.Z
4. buf-release.yml runs   → buf push --label <tag> to BSR
5. BSR publishes generated code for downstream consumers
6. Backend/frontend update deps to consume new types
```

**Cross-repo dependency order** (strict):
```
specification PR merge → Release → BSR gen
    ├── backend can now build with new proto types
    └── frontend can now build with new proto types
```

Backend and frontend PRs may be created as **drafts** before BSR gen completes, but they will not build until the new types are published.

## Pre-implementation Checklist

Before modifying `.proto` files, read:
1. `docs/product-design.md` — domain concepts and product vision
2. This file — project rules and core design constraints
