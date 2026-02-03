---
name: protobuf-development-workflow
description: Development workflow, CLI tools, and CI/CD for Liverty Music. Use this when setting up environments, running checks, or debugging CI.
---

# Protobuf Development Workflow

## Goal

Manage the local and CI development lifecycle for Protocol Buffers within the Liverty Music project.

## Instructions

1.  **Environment Setup**:
    - **Manager**: `mise` manages all tools.
    - **Install**: Run `mise install` in root.
    - **Hooks**: Run `pre-commit install`.

2.  **Local Development Loop**:
    - **Lint**: `buf lint`
    - **Format**: `buf format -w`
    - **Breaking Change**: `buf breaking --against '.git#branch=main'`

3.  **Pre-commit Hooks**:
    - Commit: `buf lint`, `buf format`, breaking change detection, prettier.
    - Push: Schemas pushed to BSR for remote code generation.

4.  **CI/CD Pipeline**:
    - **PR Workflow** (`.github/workflows/buf-pr-checks.yml`):
      - Runs on all PR events including label changes.
      - Validates: lint, format (`--diff --exit-code`), breaking changes, dry-run generation.
    - **Release Workflow** (`.github/workflows/buf-release.yml`):
      - Triggers on GitHub releases.
      - Automatic `buf push` with release tag as BSR label.
      - Requires `BUF_TOKEN` secret.

## Constraints

- Do NOT bypass `pre-commit` hooks.
- Do NOT use global `buf` installation; use `mise` version.
- Do NOT run `buf generate` EVER. Local generation is strictly forbidden to ensure consistency with BSR.

## Example

```bash
# Workflow for a new change
mise install
buf lint && buf format -w
buf breaking --against '.git#branch=main'
git add .
git commit -m "feat: updates"
```
