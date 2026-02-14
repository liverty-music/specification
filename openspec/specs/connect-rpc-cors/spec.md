## ADDED Requirements

### Requirement: CORS Middleware for Connect-RPC
The system SHALL implement Cross-Origin Resource Sharing (CORS) middleware in the Connect-RPC server using the `connectrpc.com/cors` package.

#### Scenario: Preflight request handled
- **WHEN** browser sends OPTIONS request with Origin header
- **THEN** server responds with 200 OK and CORS headers (Access-Control-Allow-*)

#### Scenario: Actual request succeeds
- **WHEN** browser sends POST request to /liverty_music.rpc.*/method with correct Origin
- **THEN** request reaches handler and response includes Access-Control-Allow-Origin header

### Requirement: Allowed Origins Configuration
The system SHALL allow configurable list of allowed origins via environment variable `CORS_ALLOWED_ORIGINS`.

#### Scenario: Origin list from environment
- **WHEN** `CORS_ALLOWED_ORIGINS=https://liverty-music.app,http://localhost:5173` is set
- **THEN** requests from those origins pass CORS checks

#### Scenario: Origin not in list
- **WHEN** request Origin header is not in allowed list
- **THEN** CORS headers are not added, browser blocks request

### Requirement: Connect-RPC Protocol Headers
The system SHALL expose Connect-specific headers required by browser clients: `Connect-Protocol-Version`, `Connect-Timeout-Ms`, `Grpc-Status`, `Grpc-Message`, `Grpc-Status-Details-Bin`.

#### Scenario: Connect headers allowed
- **WHEN** browser sends request with Connect-Protocol-Version header
- **THEN** header is in CORS allowed headers list

#### Scenario: Trailers exposed
- **WHEN** unary RPC response includes trailers with Trailer- prefix
- **THEN** trailers are in ExposedHeaders list so browser JavaScript can access them

### Requirement: Authorization Header Support
The system SHALL include application-specific headers (e.g., `Authorization`) in allowed CORS headers.

#### Scenario: Bearer token accepted
- **WHEN** request includes `Authorization: Bearer <token>` header
- **THEN** Authorization is in allowed headers and request passes CORS check

### Requirement: CORS Validation at Startup
The system SHALL log warning if `CORS_ALLOWED_ORIGINS` environment variable is not set or is empty.

#### Scenario: Missing origins logged
- **WHEN** application starts without CORS_ALLOWED_ORIGINS env var
- **THEN** warning is logged to stderr/structured logs
