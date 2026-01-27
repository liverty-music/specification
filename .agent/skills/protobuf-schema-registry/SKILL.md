---
name: protobuf-schema-registry
description: BSR integration details, package names, and consumption commands. Use this when importing code, verifying dependencies, or using generated clients.
---

# Protobuf Schema Registry

## Goal

Provide details on the Buf Schema Registry (BSR) dependencies and how to consume generated code.

## Instructions

1.  **BSR Code Generation Flow**:
    - **Push**: `buf push` uploads schemas to BSR.
    - **Remote Generation**: BSR generates code using plugins in `buf.gen.yaml`.
    - **Plugins**: `protocolbuffers/go`, `connectrpc/go`, `bufbuild/es`, `bufbuild/connect-es`, `bufbuild/validate-go`.
    - **Consumer Access**: Generated code via Go modules and npm packages.

2.  **Registry URLs**:
    - Entity Schema: `buf.build/liverty-music/entity`
    - RPC Schema: `buf.build/liverty-music/rpc`

3.  **Package Constants**:
    - Entities: `liverty_music.entity.v1`
    - RPCs: `liverty_music.rpc.v1`

4.  **Consumption (Go)**:

    ```bash
    go get buf.build/gen/go/liverty-music/entity/protocolbuffers/go
    go get buf.build/gen/go/liverty-music/entity/bufbuild/validate-go
    go get buf.build/gen/go/liverty-music/rpc/protocolbuffers/go
    go get buf.build/gen/go/liverty-music/rpc/connectrpc/go
    go get buf.build/gen/go/liverty-music/rpc/bufbuild/validate-go
    ```

5.  **Consumption (TypeScript)**:
    ```bash
    npm install @buf/liverty-music_entity.bufbuild_es
    npm install @buf/liverty-music_rpc.bufbuild_es
    npm install @buf/liverty-music_rpc.bufbuild_connect-es
    ```

## Constraints

- Do NOT rely on local generation for downstream consumers.
- Always use the `liverty-music` organization in BSR.

## Example

**Adding a dependency in Go**:

```go
import (
    entityv1 "buf.build/gen/go/liverty-music/entity/protocolbuffers/go/liverty_music/entity/v1"
)
```
