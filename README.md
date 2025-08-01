# Protobuf Scaffold

A repository for managing application entity and API definitions using Protocol Buffers with Buf Schema Registry (BSR) for remote code generation.

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
├── buf.gen.yaml     # Code generation plugin configuration for BSR
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
