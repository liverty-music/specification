## ADDED Requirements

### Requirement: Diagnostic capture of error response body

When an outbound HTTP request returns a status code in the 4xx or 5xx range, the system SHALL capture a bounded portion of the response body and attach it to the resulting application error so that downstream logs preserve the upstream diagnostic message.

This requirement applies to all outbound HTTP clients: the shared `pkg/api.FromHTTP` helper used by the Google Maps, fanart.tv, Last.fm, and MusicBrainz clients, as well as any client with its own error-mapping path (e.g., the webpush sender and the fanart.tv logo fetcher).

#### Scenario: Error body is captured into the apperr

- **WHEN** an outbound HTTP request returns a status code ≥ 400
- **THEN** the system SHALL read up to the first 1024 bytes of the response body
- **AND** the system SHALL attach the captured bytes (as a UTF-8 string with non-printable bytes elided) to the resulting `apperr` via a `slog.Attr` named `responseBody`
- **AND** the system SHALL still include the `statusCode` attribute as before

#### Scenario: Body capture is bounded

- **WHEN** the upstream response body exceeds the cap
- **THEN** the system SHALL truncate to the first 1024 bytes
- **AND** the captured text SHALL be suffixed with `…` (U+2026) to indicate truncation
- **AND** the underlying response stream SHALL still be drained and closed to allow connection reuse

#### Scenario: Body capture handles empty / oversized binary bodies

- **WHEN** the upstream response body is empty
- **THEN** the system SHALL attach the `responseBody` attribute with an empty string

- **WHEN** the upstream response body contains non-UTF-8 binary content
- **THEN** the system SHALL still attach a `responseBody` attribute, with non-printable bytes replaced by the Unicode replacement character (U+FFFD) so that the structured log entry remains valid

#### Scenario: Body read failures do not mask the original error

- **WHEN** reading the response body itself fails (network error, timeout)
- **THEN** the system SHALL still return the original status-derived `apperr` with the appropriate code mapping
- **AND** the body-read failure SHALL be logged at WARN level with the original error preserved
