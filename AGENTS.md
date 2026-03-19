<poly-repo-workspace>
  <description>
    Liverty Music poly-repo workspace managed as git worktrees.
    Each repo's AGENTS.md contains detailed coding conventions.
    Read the target repo's AGENTS.md before making changes.
  </description>

  <structure>
    liverty-music/
    ├── specification/
    │   ├── openspec/changes/ ← Ongoing changes (proposals, designs, specs, tasks)
    │   ├── openspec/specs/   ← The latest capability specs
    │   └── proto/            ← Protobuf entity / RPC schema
    ├── backend/               ← Go implementation (Connect-RPC services)
    ├── frontend/              ← Aurelia 2 PWA
    └── cloud-provisioning/
        ├── src/               ← Pulumi code (GCP, Cloudflare, GitHub resources)
        └── k8s/               ← Kubernetes manifests (Kustomize base/overlays)
  </structure>

  <dependency-order>
    specification PR merge → GitHub Release → BSR gen completes
    ├── backend can now build with new proto types
    └── frontend can now build with new proto types

    Backend/frontend PRs may be created as drafts before BSR gen,
    but CI will fail until new types are published.
  </dependency-order>

  <release-process>
    1. Create PR to specification/main → buf-pr-checks.yml validates
    2. Merge PR to main
    3. Create GitHub Release (tag: vX.Y.Z) → buf-release.yml pushes to BSR
    4. BSR publishes generated code for downstream consumers
    5. Backend/frontend update deps to consume new types
  </release-process>

  <constraints>
    <forbidden repo="specification">buf push — CI-only via buf-release.yml on Release publish</forbidden>
    <forbidden repo="specification">buf generate — BSR handles remote generation</forbidden>
    <forbidden repo="backend">Local protobuf code generation — use BSR remote gen via go get</forbidden>
  </constraints>
</poly-repo-workspace>

<poly-repo-context repo="specification">
  <responsibilities>Protocol Buffers schema repository. Defines entity and RPC interfaces
  using Buf. Single source of truth for API contracts consumed by backend and frontend.
  Also hosts OpenSpec structured specification changes.</responsibilities>
  <essential-commands>
    buf lint                                  # Lint proto files
    buf format -w                             # Auto-format proto files
    buf breaking --against '.git#branch=main' # Check breaking changes
  </essential-commands>
</poly-repo-context>

<agent-rules>

## Pre-commit Hooks

Pre-commit hooks run `buf lint`, `buf format -w`, and `buf breaking` automatically on commit.
If a breaking change is intentional, add the `buf skip breaking` label to the PR.

## Architecture

### Layered Proto Structure

```
proto/liverty_music/
├── entity/v1/    # Core business entities — the domain model
│   ├── entity.proto   # Package-level doc (no messages)
│   ├── user.proto     # User, UserId, UserEmail
│   ├── artist.proto   # Artist, ArtistId, OfficialSite, Mbid
│   ├── concert.proto  # Concert, EventId, ConcertTitle
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

Generated code is hosted on BSR at `buf.build/liverty-music/schema`. Do not commit a `gen/` directory. Consumers install generated packages via `go get` or `npm install` from BSR.

## OpenSpec Workflow

This repo uses OpenSpec for structured specification changes. Changes live in `openspec/changes/` and follow an artifact workflow (proposal → design → specs → tasks). Use `/opsx:new` to start a new change and `/opsx:continue` to progress through artifacts.

## Pre-implementation Checklist

Before modifying `.proto` files, read:
1. `docs/product-design.md` — domain concepts and product vision
2. This file — project rules and core design constraints

</agent-rules>
