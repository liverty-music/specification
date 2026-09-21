<!-- spec: frontend-testing | target: components/adapter/fan/web/rpc/auth-headers | flags: CLASSNAME | new_name: gRPC transport injects auth headers -->

### Requirement: gRPC transport injects auth headers
The `authInterceptor` within `createTransport` SHALL inject a Bearer token into every outgoing gRPC request.

#### Scenario: Authenticated user has valid token
- **WHEN** the current authentication session yields a user with an `access_token`
- **THEN** the interceptor SHALL add `Authorization: Bearer <token>` to the request headers

#### Scenario: No authenticated user
- **WHEN** the current authentication session yields no user (`null`)
- **THEN** the interceptor SHALL NOT add an Authorization header
