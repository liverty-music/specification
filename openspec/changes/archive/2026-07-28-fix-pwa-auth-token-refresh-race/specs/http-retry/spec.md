## MODIFIED Requirements

### Requirement: Deduplicated auth token refresh on concurrent 401s
The auth retry interceptor SHALL deduplicate concurrent `signinSilent()` calls. If a token refresh is already in progress when a second `Unauthenticated` error is received, the second interceptor SHALL await the in-progress refresh rather than issuing a new one.

**Rationale**: With Zitadel refresh token rotation, concurrent `signinSilent()` calls using the same refresh token result in `RefreshTokenInvalid (400)` — the first use rotates the token and the second is rejected. A singleton promise ensures the refresh token is used at most once per expiry cycle.

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
