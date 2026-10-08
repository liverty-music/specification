# liverty-music/specification

A repository for managing application entity and API definitions using Protocol Buffers with Buf Schema Registry (BSR) for remote code generation.

## Development workflow (all liverty-music repositories)

This repository is also the **OpenSpec store** `openspec-store`: every spec and change for `specification`, `backend`, `frontend` and `cloud-provisioning` lives under [`openspec/`](openspec/). The other three repositories only carry a pointer (`openspec/config.yaml` with `store: openspec-store`), so any `openspec` command run there resolves here. The workflow below needs nothing beyond [Claude Code](https://code.claude.com/docs), the [OpenSpec CLI](https://github.com/Fission-AI/OpenSpec) and `gh`, and works the same on a laptop and in Claude Code on the web.

### Lifecycle of a change

1. **Plan** in this repository: `/opsx:propose <change>` writes `openspec/changes/<change>/` (proposal, design, delta specs, tasks). Split `tasks.md` by repository. Open the PR from a worktree (see [Branch work in this repository](#branch-work-in-this-repository)), review it as a normal PR and merge it; the *OpenSpec Checks* workflow validates it, and a change that modifies existing requirements carries `openspec show <change> --diff` in the PR body.
2. **Implement** in each affected repository, one Claude session per repository (each session only loads its own repository's `AGENTS.md`). Start with `/opsx:apply <change>`; it reads the change from the store. Task check-offs and spike results land directly in the `specification` checkout's working tree (on `main`, uncommitted) through the store pointer; nothing in that checkout is committed until close-out.
3. **Proto first** when the contract changes: the `specification` PR merges, a GitHub Release (`vX.Y.Z`) triggers BSR generation, then `backend` / `frontend` consume the generated types. Downstream work starts early against placeholder types; see [AGENTS.md](AGENTS.md) for the rules.
4. **Open one PR per repository.** Every PR fills the *OpenSpec Traceability* section of its template (`OpenSpec-Change`, store commit). Merge order: `specification` → Release/BSR → `backend` / `frontend`; `cloud-provisioning` is independent.
5. **Close out** here once the implementation PRs have merged and the release is confirmed in production: `/opsx:verify <change>`, then archive in a worktree that carries the change's latest progress, committing only that change's paths:

   ```bash
   S=<path-to-this-checkout>
   git -C "$S" fetch origin
   git -C "$S" worktree add .claude/worktrees/<change>-archive -b <change>-archive origin/main
   cd "$S/.claude/worktrees/<change>-archive"
   rsync -a --delete "$S/openspec/changes/<change>/" openspec/changes/<change>/   # the progress /opsx:apply recorded
   openspec archive <change>
   git add openspec/changes/<change> openspec/changes/archive openspec/specs
   git commit && git push -u origin <change>-archive && gh pr create
   ```

   After it merges, sync this checkout (see below) and remove the worktree.

   One `specification` PR per change, at archive time. CI rejects an archive whose `tasks.md` still has unchecked tasks, or whose added or modified scenarios have no `@spec`-annotated test on the implementing repositories' `main`.

### Branch work in this repository

This checkout is the store. It stays on `main` and holds the uncommitted progress of every change in flight, so it never switches branches. Everything that needs a branch here — a plan PR, a proto PR, an archive — happens in a worktree cut from `origin/main`:

```bash
S=<path-to-this-checkout>
git -C "$S" fetch origin
git -C "$S" worktree add .claude/worktrees/<branch> -b <branch> origin/main
cd "$S/.claude/worktrees/<branch>"
```

- **Plan PR:** copy the change in with `cp -r "$S/openspec/changes/<change>" openspec/changes/`, then commit, push and open the PR.
- **Proto or docs PR:** edit in the worktree directly.
- **Archive:** step 5 above.

Commit hooks and `openspec archive` run in the worktree, so run them from inside it. The scenario coverage check finds the implementing repositories next to this checkout, wherever the worktree is.

After the PR merges, sync this checkout. Touch only that change's paths, because the rest of the working tree is other changes' progress:

```bash
cd "$S" && git fetch origin
# plan PR: move the untracked copy aside so the committed one can land, then restore the progress on top
mv openspec/changes/<change> /tmp/<change> && git merge --ff-only origin/main && cp -r /tmp/<change>/. openspec/changes/<change>/
# archive PR: drop the archived change's leftover edits, then fast-forward
git restore --worktree -- openspec/changes/<change> && git merge --ff-only origin/main
git worktree remove .claude/worktrees/<branch>
```

`git merge --ff-only` stops when another change's untracked plan was merged upstream and not yet synced. That change's owner syncs it as above.

### Local setup (once per machine)

```bash
npm install -g @fission-ai/openspec@1.13.2      # the version the committed /opsx files were generated with
L=~/dev/src/github.com/liverty-music           # any layout works; siblings are just convenient
for r in specification backend frontend cloud-provisioning; do gh repo clone liverty-music/$r "$L/$r"; done
openspec store register "$L/specification" --id openspec-store
openspec config set defaultStore openspec-store  # optional: resolve to the store from anywhere
```

Keep this checkout of `specification` on `main` and update it with `git fetch origin && git merge --ff-only origin/main` before planning or implementing (not `git pull`, which rebases and can autostash other changes' progress): it *is* the store, and OpenSpec never pulls for you. `openspec doctor` from any repository reports whether the store resolves.

### Local: parallel work with worktrees

Worktrees are for the implementation repositories only. `specification` stays a single checkout on `main`: every change writes to its own `openspec/changes/<change>/` folder, so parallel changes share the working tree without touching each other's files. Branch only at close-out (see *Lifecycle of a change*, step 5), and never run `git stash`, `git reset --hard`, `git restore .` or `git clean` there: they discard other changes' progress.

Use Claude Code's built-in worktrees, one per implementation repository you touch. Each lands in `<repo>/.claude/worktrees/<change>/` on branch `worktree-<change>` (rename it before pushing if you like):

```bash
cd "$L/backend"  && claude --worktree <change>    # one terminal per repository
cd "$L/frontend" && claude --worktree <change>
```

Gitignored files a worktree needs (e.g. the Playwright auth session in `frontend`) are copied in automatically via each repository's `.worktreeinclude`. To see all the worktrees together with the store in one VS Code window, compose an OpenSpec workset. The first member is where VS Code's terminal and the Claude panel start, so list an implementation worktree first:

```bash
openspec workset create <change> --tool code \
  --member frontend="$L/frontend/.claude/worktrees/<change>" \
  --member backend="$L/backend/.claude/worktrees/<change>" \
  --member specification="$L/specification"
openspec workset open <change>
```

Clean up by exiting each Claude session (it offers to remove a clean worktree and warns about uncommitted or unpushed work), then `openspec workset remove <change> --yes`.

### Cloud: Claude Code on the web

Use a **Claude Project** that contains all four repositories: each thread clones them side by side and loads every repository's `CLAUDE.md`, skills and `/opsx:*` commands. Install the Claude GitHub App on the repositories so threads can push.

- **Environment setup script** (Project settings → Environment), Trusted network access is enough:

  ```bash
  npm install -g @fission-ai/openspec@1.13.2
  ```

- **Store registration** happens at the start of a thread, because the clone path is only known then. From inside any repository clone:

  ```bash
  openspec doctor   # if openspec-store is not registered:
  openspec store register "$(git rev-parse --show-toplevel)/../specification" --id openspec-store
  ```

  In a single-repository session without a `specification` clone, clone it anywhere first (`git clone --depth 1 https://github.com/liverty-music/specification.git /tmp/openspec-store`) and register that path.
- **One repository per thread** for implementation, matching the local rule. Threads push only their own working branch.
- **No repository hooks run** in multi-repository threads (Claude Code reads no repository's `.claude/settings.json` there), so the pre-commit gate does not fire: run `make check` in the repository before committing. CI remains the gate on every PR.
- Plan and archive in a thread whose working repository is `specification`, exactly as locally.

## Prerequisites

- [mise](https://mise.jdx.dev/) must be installed
- [pre-commit](https://pre-commit.com/) must be installed

## Setup

1. Install dependencies:

```bash
mise install
```

2. Verify buf is available:

```bash
buf --version
```

3. Install pre-commit hooks:

```bash
pre-commit install
pre-commit install --hook-type pre-push
```

## Usage

### Code Generation with BSR

This repository uses **Buf Schema Registry (BSR)** for remote code generation. Generated code is available from `buf.build/pannpers/scaffold` and consumed via language-specific package managers.

**Note:** Schemas are automatically pushed to BSR via GitHub Actions during releases. Local `buf push` is prohibited to maintain version control and prevent unauthorized schema updates.

#### Consuming Generated Code

**Go:**
```bash
go get buf.build/gen/go/pannpers/scaffold/protocolbuffers/go
go get buf.build/gen/go/pannpers/scaffold/connectrpc/go
go get buf.build/gen/go/pannpers/scaffold/bufbuild/validate-go
```

**TypeScript:**
```bash
npm install @buf/pannpers_scaffold.bufbuild_es
npm install @buf/pannpers_scaffold.bufbuild_connect-es
```

### Lint

```bash
buf lint
```

### Check Breaking Changes

```bash
buf breaking --against '.git#branch=main'
```

### Format

```bash
buf format -w
```

## Pre-commit Hooks

This repository uses pre-commit hooks to ensure code quality:

### Commit-time hooks:

- **buf-lint**: Checks Protocol Buffers files for style and best practices
- **buf-format**: Automatically formats Protocol Buffers files
- **buf-breaking**: Detects breaking changes in Protocol Buffers
- **prettier**: Formats TypeScript/JavaScript files
- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with a newline
- **check-yaml**: Validates YAML files
- **check-added-large-files**: Prevents large files from being committed

### Push-time hooks:

- **buf-lint**: Additional validation on push to ensure schemas are ready for release

The commit and push hooks run automatically to ensure code quality. BSR synchronization happens only during GitHub releases via CI.

## Directory Structure

```
.
├── .mise/           # mise configuration
├── proto/           # Protocol Buffers definitions
│   └── scaffold/    # Main schema definitions
│       ├── pannpers/
│       │   ├── entity/  # Entity definitions (User, Post, etc.)
│       │   └── api/     # Service definitions
│       └── buf.yaml     # Module configuration
├── buf.yaml         # Workspace configuration
├── .pre-commit-config.yaml  # pre-commit configuration
└── README.md        # This file
```

**Note:** Generated code is hosted on BSR at `buf.build/pannpers/scaffold` and consumed via package managers. No local `gen/` directory is needed.

## Development Flow

1. Create or modify `.proto` files in the `proto/scaffold/pannpers/` directory
2. Commit changes (commit hooks will validate and format automatically)
3. Push to repository (push hooks will run additional validation)
4. Create a GitHub release with semantic version tag (e.g., `v1.0.0`)
5. GitHub Actions automatically pushes schemas to BSR with the release label
6. Generated code becomes available at `buf.build/pannpers/scaffold` with version tags
7. Consumers can update their dependencies to get the latest generated code

## GitHub Actions Automation

### Pull Request Validation
- Automatic buf lint and format validation
- Breaking change detection against base branch
- Dry-run code generation validation

### Release Automation
When you create a GitHub release:
1. GitHub Actions automatically runs `buf push --label <version>` to BSR
2. BSR generates code with the release label
3. Consumers can reference specific versions in their dependencies

## BSR Setup

This repository is configured to push to `buf.build/pannpers/scaffold`. Generated code uses these plugins:
- `buf.build/protocolbuffers/go` - Standard Go protobuf generation
- `buf.build/connectrpc/go` - Connect RPC Go bindings
- `buf.build/bufbuild/es` - TypeScript protobuf generation
- `buf.build/bufbuild/connect-es` - Connect RPC TypeScript bindings
- `buf.build/bufbuild/validate-go` - Go validation code generation
