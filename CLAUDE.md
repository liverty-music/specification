# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development Setup
```bash
mise install          # Install dependencies (buf, pre-commit)
pre-commit install     # Install commit hooks
pre-commit install --hook-type pre-push  # Install push hooks
```

### Code Generation (BSR)
```bash
buf push               # Push schema to BSR which generates code remotely
```

### Validation and Formatting
```bash
buf lint               # Lint Protocol Buffers files
buf format -w          # Format protobuf files in place
buf breaking --against '.git#branch=main'  # Check for breaking changes
```

### Verification
```bash
buf --version          # Verify buf is available
```

## Architecture Overview

This is a Protocol Buffers scaffold repository that uses Buf Schema Registry (BSR) for remote code generation from protobuf definitions. The architecture follows a clear separation between entity definitions and API service definitions.

### Key Structure
- **Entity Layer**: Core business entities defined in `pannpers/entity/v1/` (e.g., Post, User)
- **API Layer**: Service definitions in `pannpers/api/v1/` that use entity types
- **Generated Code**: Available from BSR at `buf.build/pannpers/scaffold` (no local generation)

### BSR Code Generation Flow
The repository uses Buf Schema Registry (BSR) with remote code generation:
- **Push to BSR**: `buf push` uploads schemas to `buf.build/pannpers/scaffold`
- **Remote Generation**: BSR generates code using plugins defined in `buf.gen.yaml`
- **Consumer Access**: Generated code available via Go modules and npm packages
- **Plugins Used**:
  - `buf.build/protocolbuffers/go` - Standard Go protobuf generation
  - `buf.build/connectrpc/go` - Connect RPC Go bindings
  - `buf.build/bufbuild/es` - TypeScript protobuf generation
  - `buf.build/bufbuild/connect-es` - Connect RPC TypeScript bindings
  - `buf.build/bufbuild/validate-go` - Go validation code generation

### Proto Package Structure
- `pannpers.entity.v1` - Core entities (Post, User, value objects)
- `pannpers.api.v1` - Service definitions that reference entities
- Uses proper import paths and Go package declarations

### Automated Workflow
The repository uses multiple automation layers for quality control and deployment:

#### Pre-commit Hooks
- **Commit hooks**: buf lint, format, breaking change detection, prettier
- **Push hooks**: Push schemas to BSR for remote code generation

#### GitHub Actions
- **PR Workflow** (`.github/workflows/buf-pr-checks.yml`): Runs on all PR events including label changes
  - Buf lint validation
  - Format checking with `buf format --diff --exit-code`
  - Breaking change detection against base branch
  - Dry-run code generation validation
- **Release Workflow** (`.github/workflows/buf-release.yml`): Runs when GitHub releases are published
  - Automatic `buf push` with release tag as BSR label
  - Requires `BUF_TOKEN` secret for BSR authentication

### Key Files
- `buf.yaml` - Buf v2 configuration with googleapis dependencies
- `buf.gen.yaml` - Code generation plugin configuration for BSR
- `.pre-commit-config.yaml` - Hook definitions for quality gates
- `.mise/config.toml` - Tool version management
- `.github/workflows/buf-pr-checks.yml` - GitHub Actions for PR validation
- `.github/workflows/buf-release.yml` - GitHub Actions for release automation

### Using Generated Code
Consumers can access generated code from BSR:

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

## Protobuf Design Guidelines

When designing entities and RPC interfaces, follow these established standards:

### Reference Documentation
- [Buf Style Guide](https://buf.build/docs/best-practices/style-guide/)
- [Buf Documentation Guidelines](https://buf.build/docs/bsr/documentation)
- [Buf Schema documentation](https://buf.build/docs/bsr/documentation/)
- [Protobuf Files and Packages](https://buf.build/docs/reference/protobuf-files-and-packages/)
- [Google AIP-190: Protobuf Design](https://google.aip.dev/190)
- [Google AIP General Guidelines](https://google.aip.dev/general)

### Naming Conventions (Buf Style Guide)
- **Packages**: Use `lower_snake_case` with version suffix (e.g., `pannpers.entity.v1`)
- **Messages**: Use `PascalCase` for message names
- **Fields**: Use `lower_snake_case` for field names
- **Services**: Use `PascalCase` with `Service` suffix (e.g., `PostService`)
- **RPCs**: Use `PascalCase` with VerbNoun pattern (e.g., `GetPost`, `CreatePost`)
- **Enums**: Names in `PascalCase`, values in `UPPER_SNAKE_CASE`
- **Zero values**: Should end with `_UNSPECIFIED`

### File Organization
- Package structure should have at least 3 components: `{org}.{purpose}.{version}`
- Directory structure should mirror package hierarchy
- One package per directory
- Use descriptive filenames in `lower_snake_case.proto`

### RPC Interface Design (Google AIP)
- **Standard Methods**: Follow standard CRUD patterns
  - `Get{Resource}` for single resource retrieval
  - `List{Resource}` for collection retrieval
  - `Create{Resource}` for resource creation
  - `Update{Resource}` for resource modification
  - `Delete{Resource}` for resource removal
- **Request/Response Messages**: Always create custom messages, avoid `Empty`
- **Resource-Oriented Design**: Structure APIs around resources, not actions
- **Field Masks**: Use for partial updates in `Update` operations
- **Pagination**: Implement for `List` operations using `page_size` and `page_token`
- **Type Safety**: Use user-defined types instead of primitive types for parameters
  - **Entity IDs**: Use `UserId`, `PostId` types instead of raw `string`
  - **Domain Values**: Use `PostTitle`, `UserName` types instead of raw `string`
  - **Consistency**: Ensure API parameters match entity field types exactly
  - **Validation**: User-defined types carry their validation rules automatically

### Entity Design Patterns
- **Value Objects**: Create dedicated message types for domain concepts (e.g., `PostId`, `PostTitle`)
- **Composition**: Reference other entities by ID, not nested objects
- **Versioning**: Plan for schema evolution with proper field numbering
- **Documentation**: Over-document with complete sentences using `//` comments

### Documentation Standards (Buf BSR Documentation)
Follow [Buf Documentation Guidelines](https://buf.build/docs/bsr/documentation) for comprehensive protobuf documentation:

#### Package Documentation
- **Package Comments**: Add clear overview comment above `package` directive in the first file
- **Purpose Description**: Explain what the package represents and its role in the system
- **Example**:
  ```protobuf
  // Package user provides definitions for user entities and related value objects.
  // This package contains core user data structures used across the application.
  package pannpers.entity.v1;
  ```

#### Message and Field Documentation
- **Message Comments**: Document each message with its purpose and usage context
- **Field Comments**: Explain each field's meaning, constraints, and relationships
- **Complete Sentences**: Use proper grammar and punctuation for all comments
- **Validation Context**: Document validation rules and their business rationale
- **Examples**:
  ```protobuf
  // User represents a registered user in the system.
  // Users are identified by a unique UUID and must have valid email addresses.
  message User {
    // User ID is required and must be a valid UUID format
    UserId id = 1;
    // User name is required and must be between 1 and 100 characters
    UserName name = 2;
    // User email is required and must be a valid email format
    UserEmail email = 3;
  }
  ```

#### Service Documentation
- **Service Overview**: Document the service's purpose and capabilities
- **RPC Methods**: Explain each method's functionality, parameters, and return values
- **Error Conditions**: Document expected error scenarios and status codes
- **Examples**:
  ```protobuf
  // UserService provides operations for managing user accounts.
  // This service handles user creation, retrieval, and basic profile management.
  service UserService {
    // GetUser retrieves a single user by their unique identifier.
    // Returns NOT_FOUND if the user does not exist.
    rpc GetUser(GetUserRequest) returns (GetUserResponse);

    // CreateUser creates a new user account with the provided information.
    // Returns ALREADY_EXISTS if a user with the same email already exists.
    rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
  }
  ```

#### Module Documentation
- **README Files**: Create `README.md` files at package level for comprehensive overviews
- **Architecture Context**: Explain how the package fits into the larger system
- **Usage Examples**: Provide practical examples of using the generated code
- **Relationship Diagrams**: Use Mermaid diagrams for complex relationships

#### Formatting Standards
- **Markdown Support**: Use CommonMark and GitHub Flavored Markdown in comments
- **Code Blocks**: Use backticks for code references and examples
- **Lists**: Use bullet points for multiple related items
- **Emphasis**: Use **bold** for important concepts and *italics* for parameters
- **Links**: Reference related messages, services, and external documentation

#### Deprecation Documentation
- **Deprecation Notices**: Clearly mark deprecated fields and messages
- **Migration Path**: Provide guidance for transitioning to new alternatives
- **Timeline**: Include deprecation timeline when known
- **Example**:
  ```protobuf
  message User {
    UserId id = 1;
    UserName name = 2;
    // DEPRECATED: Use email field instead. This field will be removed in v2.
    string old_email = 3 [deprecated = true];
    UserEmail email = 4;
  }
  ```

### Validation Rules (Protovalidate)
- **Always import**: Add `import "buf/validate/validate.proto"` to files using validation
- **Well-known Types**: Use built-in validation for common patterns:
  - **UUID**: `[(buf.validate.field).string.uuid = true]` for UUID fields
  - **Email**: `[(buf.validate.field).string.email = true]` for email addresses
  - **URI**: `[(buf.validate.field).string.uri = true]` for URIs/URLs
  - **URI Reference**: `[(buf.validate.field).string.uri_ref = true]` for URI references
  - **IP Address**: `[(buf.validate.field).string.ip = true]` for IP addresses (v4 or v6)
  - **IPv4**: `[(buf.validate.field).string.ipv4 = true]` for IPv4 addresses only
  - **IPv6**: `[(buf.validate.field).string.ipv6 = true]` for IPv6 addresses only
  - **Hostname**: `[(buf.validate.field).string.hostname = true]` for DNS hostnames
  - **Well-formed**: `[(buf.validate.field).string.well_known_regex = KNOWN_REGEX_HTTP_HEADER_NAME]` for standard patterns
- **String Constraints**: Always set reasonable limits:
  - **Length**: Use `min_len` and `max_len` for all string fields
  - **Pattern**: Use `pattern` for custom validation (regex)
  - **Well-formed**: Prefer built-in validators over custom regex when available
- **Required Fields**: Mark all mandatory fields with `[(buf.validate.field).required = true]`
- **Nested Messages**: Validation cascades to nested message fields automatically
- **Custom Constraints**: Use `pattern` for domain-specific validation rules only when built-ins don't suffice

### Validation Best Practices
- **ID Fields**: Use `uuid = true` for UUID-based identifiers instead of custom patterns
- **Email Fields**: Use `email = true` instead of regex patterns for email validation
- **Consistent Limits**: Apply consistent string length limits across similar field types
- **Error Messages**: Built-in validators provide better error messages than custom regex
- **Performance**: Built-in validators are more performant than regex patterns

### RPC Parameter Type Design
- **Never use primitive types** for domain concepts in RPC interfaces
- **Entity References**: Use `UserId user_id = 1` instead of `string user_id = 1`
- **Domain Values**: Use `PostTitle title = 1` instead of `string title = 1`
- **Benefits of user-defined types**:
  - **Type Safety**: Prevents mixing different ID types
  - **Validation**: Automatic validation rule inheritance from value objects
  - **Documentation**: Self-documenting API through meaningful type names
  - **Evolution**: Easier to change validation rules in one place
  - **Code Generation**: Better typed client code in target languages
- **Examples**:
  ```protobuf
  // ❌ Bad: Using primitive types
  message GetUserRequest {
    string user_id = 1;
  }

  // ✅ Good: Using user-defined types
  message GetUserRequest {
    entity.v1.UserId user_id = 1;
  }
  ```

### Breaking Change Management
- Always check breaking changes against main branch
- Reserve field numbers for future use
- Use `optional` fields for new additions to existing messages
- Follow semantic versioning for major breaking changes

## Development Workflow Notes

1. Proto files should be modified directly in the `proto/scaffold/` directory
2. Generated code is available from BSR, not stored locally
3. Breaking changes are checked against the main branch
4. All protobuf files are automatically formatted and linted on commit
5. Schemas are pushed to BSR automatically on push for remote code generation
6. Consumers access generated code via Go modules and npm packages from BSR

## CI/CD Setup Requirements

### GitHub Repository Secrets
To enable automatic BSR publishing on releases, configure the following secret:
- **`BUF_TOKEN`**: BSR authentication token for pushing schemas
  - Generate at: https://buf.build/settings/user (User API Tokens)
  - Required permissions: `repository:write` for `buf.build/pannpers/scaffold`

### Release Process
1. Create a GitHub release with semantic version tag (e.g., `v1.0.0`)
2. GitHub Actions automatically runs `buf push --label 1.0.0` to BSR
3. BSR generates code with the release label for consumer access
4. Consumers can reference specific versions: `@buf/pannpers_scaffold.bufbuild_es@1.0.0`
