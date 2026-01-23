<!-- OPENSPEC:START -->

# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:

- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:

- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Development Context

This is a Protocol Buffers schema repository using Buf Schema Registry (BSR).

## ⚠️ Mandatory Pre-implementation Checklist

Before writing any code or configuration, you MUST:

1.  **Check `docs/`**: Run `list_dir docs` to see currently available guides.
2.  **Read Relevant Guides**:
    - **Protobuf/gRPC**: If touching `.proto` files, YOU MUST read `docs/protobuf-guide.md`.
    - **Domain/Features**: If implementing business logic or entities, YOU MUST read `docs/product-design.md`.

## Essential Commands

### Development Setup

```bash
mise install          # Install dependencies (buf, pre-commit)
pre-commit install     # Install commit hooks
```

### Validation

```bash
buf lint               # Lint Protocol Buffers files
buf format -w          # Format protobuf files in place
buf breaking --against '.git#branch=main'  # Check for breaking changes
```

#### Handling Intentional Breaking Changes

If a breaking change is intentional (e.g., initial API definition or major version update):

1.  Create the Pull Request.
2.  Add the `buf skip breaking` label to the PR to bypass the breaking change check.

## Architecture Overview

- **Entity Layer**: Core business entities in `liverty_music/entity/v1/`
- **RPC Layer**: Service definitions in `liverty_music/rpc/v1/` using entity types
- **Generated Code**: Remote generation via BSR. No local generation.

## Key Files

- `buf.yaml`: Buf v2 configuration
- `buf.gen.yaml`: BSR code generation plugins
- `docs/protobuf-guide.md`: **Detailed Protobuf & BSR Guide** (READ THIS for details)
- `docs/product-design.md`: Product domain concepts

## Core Design Rules

> [!IMPORTANT]
> See `docs/protobuf-guide.md` for full guidelines.

1.  **No Primitives for Domain Types**: Use `UserId` (message), not `string`.
2.  **Resource Handling**: Follow Google AIP patterns (Get, List, Create, Update, Delete).
3.  **Documentation**: rigorous commenting required.

## Project Structure (Poly-repo)

This project adopts a poly-repo structure.

- **Specification**: `https://github.com/liverty-music/specification`
  - Manages SDD documentation via OpenSpec and orchestration.
- **Backend**: `https://github.com/liverty-music/backend`
  - Go backend application.
- **Cloud Provisioning**: `https://github.com/liverty-music/cloud-provisioning`
  - Infrastructure configuration management (GCP, GitHub, etc.).
