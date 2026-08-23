## Context

See proposal.md — Why. The failure is Zitadel v4.15.2+'s protected outbound HTTP
client denying the in-cluster webhook ClusterIP. Two facts shape the approach:

- **Setting `ZITADEL_HTTPCLIENT_DENYLIST` replaces the entire default list** — it
  does not merge with Zitadel's built-in defaults. The upstream `defaults.yaml`
  even carries a "CRITICAL SECURITY NOTE: Do not remove the CIDR subnets." So any
  override MUST re-enumerate every default entry, changing only the `10.0.0.0/8`
  line.
- The webhook is reached via the `fan-api-webhook-svc` ClusterIP
  (prod `10.30.12.134`, within the Service CIDR `10.30.0.0/20`). Zitadel enforces
  the deny check pre-dial on the resolved IP, so a hostname exemption is not
  possible — only a CIDR carve-out works. This is the maintainer-endorsed
  technique (issue #12326, `NOT_PLANNED`).

The full v4.17.1 default deny list (the set to preserve):
`localhost, 0.0.0.0/8, 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16,
172.16.0.0/12, 192.168.0.0/16, 198.18.0.0/15, ::/128, ::1/128, fc00::/7,
fe80::/10`.

## Goals / Non-Goals

**Goals:**
- Restore login by making the in-cluster webhook reachable from Zitadel's
  outbound client.
- Preserve every other SSRF protection, especially the cloud metadata range
  `169.254.0.0/16`.

**Non-Goals:**
- L2 network-layer egress (Kubernetes NetworkPolicy) — deferred; L1 only.
- Any change to the backend webhook handlers or their auth model
  (`zitadel-action-webhook` is unaffected).
- Pinning the webhook Service ClusterIP (only needed for a `/32` hole, which we
  are not using).

## Decisions

### Decision 1: Carve out the `/20` Service CIDR, not the `/32` ClusterIP

Replace `10.0.0.0/8` with the 12 CIDRs that cover `10.0.0.0/8` minus
`10.30.0.0/20` (computed via `ipaddress.address_exclude`):

```
10.0.0.0/12, 10.16.0.0/13, 10.24.0.0/14, 10.28.0.0/15,
10.30.16.0/20, 10.30.32.0/19, 10.30.64.0/18, 10.30.128.0/17,
10.31.0.0/16, 10.32.0.0/11, 10.64.0.0/10, 10.128.0.0/9
```

**Why `/20` over `/32`**: A `/32` hole (`10.30.12.134/32`) is the tightest but
breaks silently if the Service is recreated and its ClusterIP is reassigned, and
would need `spec.clusterIP` pinning. The `/20` Service CIDR opens only
in-cluster, non-internet-routable ClusterIPs (4096 addresses, all cluster-owned),
survives ClusterIP reassignment, and covers any future in-cluster Target without
re-computation. The marginal SSRF exposure over `/32` is limited to other
in-cluster services, which are not an attacker-reachable pivot.

### Decision 2: Set `HTTPClient.DenyList` under `zitadel.configmapConfig`

The chart already carries Zitadel's structured config under
`zitadel.configmapConfig` (base holds `ExternalSecure`, `TLS`, `Database`,
`Notifications`, `Log`; the prod overlay adds `ExternalDomain`, `Database`
usernames). Add `HTTPClient.DenyList` there as a YAML list.
**Alternative considered**: the chart's top-level `env:` list as
`ZITADEL_HTTPCLIENT_DENYLIST` (comma-separated string). Rejected because the
`env:` list lives in `base/values.yaml` (with the `OTEL_*` vars) and Helm
*replaces* list values across values files rather than merging them — an overlay
that re-declares `env:` would drop the base OTEL vars unless it re-lists them.
`configmapConfig` is a map that deep-merges, so a per-overlay
`configmapConfig.HTTPClient.DenyList` composes cleanly with the base config and
is naturally environment-scoped. Either way the list fully replaces Zitadel's
built-in default, so all default entries must still be enumerated.

### Decision 3: Per-environment Service CIDR via overlays

The `10.30.0.0/20` value is the **prod** Service CIDR. The base value must not
hardcode a prod-specific CIDR that is wrong for dev. Set the prod-correct list in
the prod overlay (or a base value overridden per overlay). Dev's Service CIDR
must be looked up from the dev cluster and its own list computed; dev is
currently stopped, so dev is config-only and lower priority (see Open Questions).

## Risks / Trade-offs

- **Dropping a default deny entry re-opens SSRF** → The override replaces the
  whole list. Mitigation: enumerate all 13 default entries verbatim, changing
  only the `10.0.0.0/8` line; add a task to diff the final list against the
  deployed version's `defaults.yaml` and explicitly confirm `169.254.0.0/16` is
  present.
- **Zitadel upgrade adds new default deny entries we won't inherit** → Because we
  now pin the full list, a future version's new default protections are silently
  missed. Mitigation: task/checklist note to re-review this override against
  `defaults.yaml` on every Zitadel version bump.
- **`/20` exposes other in-cluster ClusterIPs to Zitadel's outbound client** →
  Accepted; these are non-internet-routable and not an external pivot. The
  metadata endpoint and all other private ranges stay denied.

## Migration Plan

1. Add `ZITADEL_HTTPCLIENT_DENYLIST` (full list with the `/20` hole) to the
   Zitadel deployment config in `cloud-provisioning`, per environment.
2. Merge → ArgoCD syncs → Zitadel pods roll with the new env.
3. Verify prod: `POST /oauth/v2/token` no longer 500s and login completes; the
   `error calling target ... address is denied` log line stops.
4. **Rollback**: revert the config commit (returns to the failing state); no data
   migration involved.

## Open Questions

- Dev Service CIDR is not retrievable while the dev cluster is stopped. The dev
  overlay value can be computed and applied when dev is next brought up; it does
  not affect the prod fix or the specs.
