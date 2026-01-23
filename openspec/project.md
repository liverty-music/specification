# Project Context

## Purpose

This repository manages the "Liverty Music" application's entity and API definitions using Protocol Buffers and Buf Schema Registry (BSR). It serves as the single source of truth for the system's data structures and RPC interfaces, enabling remote code generation and type-safe communication between services.

## Tech Stack

- **Serialization**: Protocol Buffers (proto3)
- **Schema Registry/Tooling**: Buf (BSR, Lint, Format, Breaking)
- **RPC Framework**: Connect (Go, TypeScript)
- **Languages**: Go (Backend/Service), TypeScript (Frontend/Client)
- **Validation**: Protovalidate
- **CI/CD**: GitHub Actions

## Project Conventions

### Code Style

- **Protobuf**: Follows [Buf Style Guide](https://buf.build/docs/best-practices/style-guide/) (PascalCase messages, lower_snake_case fields).
- **Documentation**: All messages and services must have comments explaining their purpose.
- **Formatting**: Enforced via `buf format`.

### Architecture Patterns

- **Layered Design**:
  - `entity`: Core domain objects and value types (e.g., `User`, `LiveId`).
  - `rpc`: Service definitions utilizing entity types.
- **Resource-Oriented APIs**: Follows Google AIP guidance (Get/List/Create/Update/Delete).
- **Type Safety**: Use wrapper types (e.g., `UserId`) instead of primitives for identifiers.

### Testing Strategy

- **Linting**: `buf lint` runs on every commit.
- **Breaking Change Detection**: `buf breaking` checks PRs against the `main` branch.
- **Dry-run Generation**: Verifies code generation integrity during CI.

### Git Workflow

- **Pull Requests**: Validated by automated checks (Lint, Format, Breaking).
- **Releases**: Semantic version tags (e.g., `v1.0.0`) trigger automatic BSR schema pushing.
- **Main Branch**: Always stable; represents the current deployed schema state.

## Domain Context

**Liverty Music** is a personalized concert notification platform.

- **Core Entities**:
  - `User`: The music fan receiving notifications.
  - `Concert`: A music event (formerly 'Live').
  - `Artist`: The performer.
- **Goal**: Deliver timely and relevant information to users about live events they care about.

## Important Constraints

- **Remote Generation**: Code is generated remotely via BSR (`buf.build/liverty-music/...`). Do not commit generated code (`gen/`) to the repository.
- **Versioning**: Breaking changes must be managed carefully; use strict semantic versioning.

## External Dependencies

- **Buf Schema Registry (BSR)**: `buf.build` for hosting repositories and plugins.
- **Google APIs**: `googleapis` for common types and annotations.
