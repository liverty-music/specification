## Why

The Zitadel upgrade to v4.17.1 (from v4.14.0) crossed v4.15.2, which introduced a
protected outbound HTTP client (`HTTPClient.DenyList`, CVE-2026-55671 SSRF
hardening) that **denies all RFC1918 ranges by default**. Zitadel's Actions v2
webhook Targets are dialed through this client, so both in-cluster Target calls
(`/pre-access-token` and `/account-login-event`, served by
`fan-api-webhook-svc` at a `10.30.0.0/20` ClusterIP) are now refused with
`address is denied by '10.0.0.0/8'`. The `pre-access-token` Target runs during
token issuance, so `POST /oauth/v2/token` returns **500 Internal Server Error**
and **every user login fails**. This is a live production outage introduced by
today's upgrade.

## What Changes

- Override Zitadel's `HTTPClient.DenyList` (env `ZITADEL_HTTPCLIENT_DENYLIST`)
  in the Zitadel deployment config so the in-cluster webhook Service CIDR
  (`10.30.0.0/20`) is reachable, while every other default deny entry is
  preserved.
  - The `10.0.0.0/8` entry is replaced by the 12 CIDRs produced by excluding
    `10.30.0.0/20` from `10.0.0.0/8`, keeping the rest of the `10/8` space denied.
  - **Metadata endpoint stays denied**: `169.254.0.0/16` (covers the GCP
    metadata server `169.254.169.254`) remains in the deny list, as do
    `127.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, and the default IPv6 ranges.
- Scope: **L1 (application-layer) only**. No Kubernetes NetworkPolicy / egress
  work in this change.
- This is a **permanent** configuration, not a temporary workaround: upstream
  issue [#12326](https://github.com/zitadel/zitadel/issues/12326) requesting an
  AllowList / per-target exemption was closed `NOT_PLANNED`, and the maintainers
  endorse the CIDR-hole technique as the supported solution.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `zitadel-self-hosted-deployment`: Add a requirement that Zitadel's outbound
  protected HTTP client permits the in-cluster webhook Service CIDR while
  retaining SSRF protection for all other private ranges and the cloud metadata
  endpoint.

## Impact

- **Repo**: `cloud-provisioning` — Zitadel Helm values / configmap env
  (`k8s/namespaces/zitadel/...`), no application code.
- **Affected flow**: OIDC token issuance (`/oauth/v2/token`) and the
  `account.login` Actions v2 event → both Zitadel Actions v2 Targets defined in
  `src/zitadel/components/actions-v2.ts` (`pre-access-token-webhook`,
  `login-event-webhook`), both dialing `fan-api-webhook-svc`.
- **Blast radius**: Fixes total login outage in prod. The un-denied
  `10.30.0.0/20` range contains only in-cluster (non-internet-routable) Service
  ClusterIPs; the cloud metadata endpoint and all other private ranges remain
  denied.
- **Dev**: `10.30.0.0/20` is the prod Service CIDR; the dev overlay must use its
  own Service CIDR value (dev env is currently stopped, so verification is
  config-review only).
