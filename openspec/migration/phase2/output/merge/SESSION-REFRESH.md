<!-- merge_group: SESSION-REFRESH | target: components/infrastructure/fan/web/global/app-shell | members: 2 -->
<!-- renamed_scenarios: 0 -->

### Requirement: Deduplicated auth token refresh on Unauthenticated errors

The auth retry interceptor SHALL intercept `Code.Unauthenticated` errors, attempt a silent OIDC token refresh, and retry the request. Concurrent `Unauthenticated` errors SHALL be deduplicated: if a token refresh is already in progress when another `Unauthenticated` error is received, the interceptor handling it SHALL await the in-progress refresh rather than issuing a new one, so that at most one refresh is initiated per expiry cycle.

#### Scenario: Silent refresh succeeds and request is retried
- **WHEN** a gRPC call returns `Code.Unauthenticated`
- **THEN** the interceptor SHALL call `signinSilent()` and retry the original request

#### Scenario: Silent refresh fails and user is redirected
- **WHEN** a gRPC call returns `Code.Unauthenticated` and `signinSilent()` throws
- **THEN** the interceptor SHALL redirect to `/welcome`

#### Scenario: Non-auth errors pass through
- **WHEN** a gRPC call returns an error code other than `Unauthenticated`
- **THEN** the interceptor SHALL re-throw the error without interception

#### Scenario: Single RPC gets Unauthenticated
- **WHEN** one RPC returns `Unauthenticated` and no refresh is in progress
- **THEN** the interceptor SHALL call `signinSilent()` and await the result
- **AND** on success, retry the original RPC with the new access token
- **AND** on failure, clear the user session and redirect to `/welcome`

#### Scenario: Multiple concurrent RPCs all get Unauthenticated
- **WHEN** two or more in-flight RPCs simultaneously receive `Unauthenticated`
- **THEN** exactly one `signinSilent()` request SHALL be sent to Zitadel
- **AND** all concurrent interceptors SHALL await the same refresh promise
- **AND** on success, each interceptor SHALL retry its original RPC with the new token
- **AND** on failure, the user session SHALL be cleared and the user redirected to `/welcome`

#### Scenario: Subsequent expiry after refresh completes
- **WHEN** a token refresh completes and the singleton promise is cleared
- **AND** the new access token later expires
- **THEN** the next `Unauthenticated` response SHALL start a new `signinSilent()` call
