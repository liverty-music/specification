<poly-repo-workspace>
  <description>
    Liverty Music poly-repo workspace: four GitHub repositories worked on side by
    side, locally or in Claude Code on the web. Each repo's AGENTS.md contains
    detailed coding conventions. Read the target repo's AGENTS.md before making changes.
    All planning (OpenSpec specs and changes) lives in this repository, which is
    registered as the OpenSpec store `openspec-store`. backend, frontend and
    cloud-provisioning carry no planning of their own: their `openspec/config.yaml`
    declares `store: openspec-store`, so every `openspec` command run there resolves here.
  </description>

  <structure>
    liverty-music/
    ├── specification/         ← OpenSpec store "openspec-store" (.openspec-store/store.yaml)
    │   ├── openspec/changes/ ← Ongoing changes (proposals, designs, specs, tasks)
    │   ├── openspec/specs/   ← The latest specs: stories/ + components/{entity,usecase,adapter,infrastructure}/
    │   └── proto/            ← Protobuf entity / RPC schema
    ├── backend/               ← Go implementation (Connect-RPC services)
    ├── frontend/              ← Aurelia 2 PWA
    └── cloud-provisioning/
        ├── src/               ← Pulumi code (GCP, Cloudflare, GitHub resources)
        └── k8s/               ← Kubernetes manifests (Kustomize base/overlays)
  </structure>

  <workflow>
    Full human-readable version: README.md "Development workflow". Needs only
    Claude Code, the OpenSpec CLI (1.13.2) and gh; no machine-specific tooling.
    1. Plan here: /opsx:propose <change>, tasks split by repository, PR, merge.
    2. Implement one Claude session per affected repository (only that repo's
       AGENTS.md is loaded): /opsx:apply <change>. Locally, isolate with
       `claude --worktree <change>` (<repo>/.claude/worktrees/<change>, branch
       worktree-<change>); gitignored files come in via .worktreeinclude.
       Optionally view all worktrees + the store with `openspec workset`.
    3. Proto first when the contract changes (see dependency-order below).
    4. One PR per repository, each citing the change in its OpenSpec
       Traceability section.
    5. After the implementation PRs merge: /opsx:verify then /opsx:archive here.
    Cloud (Claude Project with all four repos): the environment setup script
    installs the OpenSpec CLI; at thread start run `openspec doctor` and, if the
    store is missing, `openspec store register <path-to-specification-clone>
    --id openspec-store`. Multi-repo threads run no repository hooks, so run
    `make check` before committing; CI is the gate.
  </workflow>

  <dependency-order>
    specification PR merge → GitHub Release → BSR gen completes
    ├── backend can now build with new proto types
    └── frontend can now build with new proto types

    Backend/frontend PRs must NOT be opened (even as drafts) before BSR gen
    completes — CI would fail on the missing types and create review noise.
    Prepare branches locally; push only after the generated package is
    upgraded and the placeholder types are swapped (see downstream-implementation).
    EXCEPTION: open a draft early only when the user explicitly requests
    parallel review, annotating the description with "Depends on BSR gen for vX.Y.Z".
  </dependency-order>

  <release-process>
    1. Create PR to specification/main → buf-pr-checks.yml validates
    2. Merge PR to main
    3. Create GitHub Release (tag: vX.Y.Z) → buf-release.yml pushes to BSR
    4. BSR publishes generated code for downstream consumers
    5. Backend/frontend update deps to consume new types
  </release-process>

  <downstream-implementation>
    Parallelize aggressively — the specification review/CI cycle is long; do
    not let backend/frontend idle. As soon as the proto surface is agreed (an
    approved OpenSpec change or an open specification PR), start downstream work:
    - Write handler/service/UI code against the *planned* type shape, using local
      type aliases or placeholder shapes where the generated types will slot in.
    - Build repository layers, use cases, business logic, and unit tests with
      mocks — none of these depend on the generated types.
    - Mark each consumption site with a clear `TODO: swap to generated type
      after BSR gen` comment.
    After the specification Release triggers BSR gen, monitor it until success:
      gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3
      gh run watch   # if a run is in progress
    Then upgrade the generated package and swap the placeholders per each repo's
    own AGENTS.md, run `make check`, and only then push and open the PR.
  </downstream-implementation>

  <constraints>
    <forbidden repo="specification">buf push — CI-only via buf-release.yml on Release publish</forbidden>
    <forbidden repo="specification">buf generate — BSR handles remote generation</forbidden>
    <forbidden repo="backend">Local protobuf code generation — use BSR remote gen via go get</forbidden>
  </constraints>
</poly-repo-workspace>

<poly-repo-context repo="specification">
  <responsibilities>Protocol Buffers schema repository. Defines entity and RPC interfaces
  using Buf. Single source of truth for API contracts consumed by backend and frontend.
  Also the OpenSpec store `openspec-store`: hosts every spec and change for all repos.</responsibilities>
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
│   ├── concert.proto  # Concert
│   ├── event.proto    # Event, EventId
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

This repo is the OpenSpec **store** `openspec-store` (identity file: `.openspec-store/store.yaml`). Every change and spec for backend, frontend, cloud-provisioning and this repo lives under `openspec/` here; the other repos only carry a pointer (`openspec/config.yaml` with `store: openspec-store`). Changes follow the artifact workflow (proposal → design → specs → tasks) via the `/opsx:*` commands.

- **Inside this repo** commands resolve to the local `openspec/` root as usual. **Anywhere else** they resolve through the store registry; pass `--store openspec-store` when in doubt. The `Using OpenSpec root: openspec-store` banner confirms which root is in use.
- **Per-machine registration** (once per laptop, or at the start of every cloud thread): `openspec store register <path-to-this-checkout> --id openspec-store`. `openspec doctor` reports a missing registration; in a cloud thread the sibling `specification` clone is the path to register. Keep the registered checkout on `main` and pull it before planning: OpenSpec never pulls.
- **Task progress and archive are recorded here.** Implementation repos never write to the store; their PRs cite the change (`OpenSpec-Change: <id>`) and the store commit they were built against, and the change is verified/archived in this repo once those PRs merge.
- **Sharing is plain git.** OpenSpec never pulls or pushes; commit and push planning like code, and review it via PRs on this repo.
- **Plan PR bodies show real spec diffs.** When a change carries `MODIFIED`, `REMOVED` or `RENAMED` requirements, append the part of `openspec show <change> --diff` from `Specifications Changed (diffs)` onward to the PR body inside a collapsed `<details>` block (the PR file diff only shows the delta file, not what it changes in the main spec). Skip it for changes that only add requirements. Refresh it with `gh pr edit` whenever the artifacts change during review.
- **CI gate (`.github/workflows/openspec-checks.yml`)** runs on every PR touching `openspec/`: `openspec validate --all`, `openspec validate --changes --strict`, and a check that every change archived in the PR has all tasks checked. It is the only gate in cloud threads, where repository hooks do not run.

### Spec tree

Specs follow the `liverty-clean-arch` schema (`openspec/schemas/liverty-clean-arch/`), whose `specs` instruction is the authoritative description of the tree and the writing rules. In short:

- `specs/stories/<story>/` — one user goal, named as a verb phrase, verified end to end.
- `specs/components/entity/<entity>/` — the ubiquitous language; language-independent, proto/Go/TS are derived from it. Write entities first.
- `specs/components/usecase/<entity>/<method>/` — one exported usecase method each.
- `specs/components/{adapter,infrastructure}/<audience>/<web|api>/.../<component>/` — outer layers, always from one audience's point of view (`fan`, `admin`, `organizer`); flows that cross audiences are stories.
- Only product behavior belongs in a spec. CI, deployment, code conventions and implementation design go in the change's `design.md` or outside OpenSpec. Subjects are entities, interfaces, routes, surfaces and ubiquitous-language nouns, never implementation types or file paths; thresholds are numbers.
- `scripts/check-spec-layout.py` (pre-commit) rejects any spec outside this layout.

## Pre-implementation Checklist

Before modifying `.proto` files, read:
1. `docs/product-design.md` — domain concepts and product vision
2. This file — project rules and core design constraints

## Review criteria (flag violations)

- Domain concepts are wrapper messages with protovalidate (`UserId`, `VenueName`…), never bare `string`/`int` (cf. `entity/v1/*.proto`).
- `entity/v1/` holds pure data types (no service logic); `rpc/*/v1/` imports entities and follows Google AIP.

</agent-rules>
