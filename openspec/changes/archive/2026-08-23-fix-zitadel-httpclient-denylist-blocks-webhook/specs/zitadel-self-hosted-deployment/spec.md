## ADDED Requirements

### Requirement: Outbound HTTP Client Permits In-Cluster Webhook Targets While Retaining SSRF Protection

Zitadel's protected outbound HTTP client (the deny list that governs Actions v2
Target calls, `HTTPClient.DenyList` / env `ZITADEL_HTTPCLIENT_DENYLIST`) SHALL be
configured so that the in-cluster webhook Service CIDR (`fan-api-webhook-svc`,
prod `10.30.0.0/20`) is reachable, while all other RFC1918 private ranges, the
loopback range, and the cloud metadata range remain denied. Concretely, the
default `10.0.0.0/8` entry SHALL be replaced by the exact set of CIDRs that
covers `10.0.0.0/8` **minus** the webhook Service CIDR, and every other default
deny entry — `127.0.0.0/8`, `169.254.0.0/16` (which covers the cloud metadata
endpoint `169.254.169.254`), `172.16.0.0/12`, `192.168.0.0/16`, and the default
IPv6 ranges — SHALL be retained.

**Rationale**: Zitadel v4.15.2+ denies all RFC1918 ranges by default (SSRF
hardening, CVE-2026-55671) and routes Actions v2 Target calls through this
client. The in-cluster webhook is dialed on a private ClusterIP, so without an
exemption the deny list blocks token issuance and breaks all logins. Upstream
[#12326](https://github.com/zitadel/zitadel/issues/12326) requesting an AllowList
was closed `NOT_PLANNED`; the maintainer-endorsed technique is to punch a CIDR
hole in the deny list for the trusted target. The hole is scoped to the Service
CIDR (not `10.0.0.0/8` wholesale) so the exposure is limited to
in-cluster-only ClusterIPs, and the metadata endpoint stays denied.

#### Scenario: In-cluster Actions v2 Target call succeeds

- **WHEN** Zitadel dials an Actions v2 Target at
  `http://fan-api-webhook-svc.backend.svc.cluster.local:9090` (paths
  `/pre-access-token` or `/account-login-event`), resolving to a ClusterIP within
  the webhook Service CIDR
- **THEN** the outbound HTTP client SHALL NOT deny the dial on the basis of the
  destination being a private address
- **AND** the request SHALL reach the backend webhook handler

#### Scenario: Token issuance completes with the pre-access-token Target enabled

- **WHEN** a user completes authentication and `POST /oauth/v2/token` triggers the
  `pre-access-token` Actions v2 Target
- **THEN** the Target call SHALL succeed and the token endpoint SHALL return a
  successful response rather than HTTP 500 `Errors.Internal`

#### Scenario: Cloud metadata endpoint remains denied

- **WHEN** an outbound HTTP request from Zitadel targets the cloud metadata
  endpoint `169.254.169.254` (or any address in `169.254.0.0/16`)
- **THEN** the outbound HTTP client SHALL deny the dial

#### Scenario: Non-webhook private ranges remain denied

- **WHEN** an outbound HTTP request from Zitadel targets a private address outside
  the webhook Service CIDR — including any `172.16.0.0/12`, `192.168.0.0/16`,
  `127.0.0.0/8`, or the remainder of `10.0.0.0/8` not covered by the webhook
  Service CIDR
- **THEN** the outbound HTTP client SHALL deny the dial
