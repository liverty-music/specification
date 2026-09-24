<!-- spec: frontend-testing | target: components/adapter/fan/web/rpc/auth-headers | flags: CLASSNAME | new_name: gRPC transport injects auth headers -->
<!-- implementation names to remove: getUserManager -->

### Requirement: gRPC transport injects auth headers
The `authInterceptor` within `createTransport` SHALL inject a Bearer token into every outgoing gRPC request.

#### Scenario: Authenticated user has valid token
- **WHEN** `getUserManager().getUser()` returns a user with an `access_token`
- **THEN** the interceptor SHALL add `Authorization: Bearer <token>` to the request headers

#### Scenario: No authenticated user
- **WHEN** `getUserManager().getUser()` returns `null`
- **THEN** the interceptor SHALL NOT add an Authorization header
