## Context

During end-to-end validation of the `scope-new-concert-notifications` change, smoke testing the new `NotifyNewConcerts` debug RPC against dev returned HTTP 200 from the RPC but logged `push service returned status 403` for every individual webpush delivery. The on-call session that followed traced the cause through 5 hypotheses (VAPID key mismatch, VAPID rotation drift, in-app browser vs Chrome subscription divergence, FCM legacy URL deprecation, VAPID JWT clock skew) before isolating the actual issue:

1. The deployed VAPID public key, derived public from the Secret Manager private key, the K8s ConfigMap value, and the Vite-baked frontend bundle value were verified byte-identical via cryptographic derivation (`crypto/elliptic.P256().ScalarBaseMult`).
2. A direct CLI call to the same FCM endpoint with the same VAPID credentials from the operator's local network returned `201 Created` (success). The same call routed through the `server-app` pod returned `403`.
3. A bare `kubectl run --image=curlimages/curl ... -- curl https://fcm.googleapis.com/fcm/send/<token>` from inside the cluster returned the generic Google edge body "Your client does not have permission to get URL ... from this server. That's all we know.", which is the documented signature of the `restricted.googleapis.com` VIP rejecting non-VPC-Service-Controls services.

The official remediation is documented at <https://cloud.google.com/vpc/docs/configure-private-google-access>: switch from the restricted VIP (which enforces a VPC-SC allowlist) to the private VIP (which does not).

Two follow-on issues materially extended the time-to-diagnose and warrant being fixed in the same change:

- The webpush sender, the shared `pkg/api.FromHTTP` helper, and the fanart.tv logo fetcher all discard the upstream response body on error. Only the status code reaches the structured log. The decisive "Your client does not have permission ..." string was not visible in any production log; it was only obtained by issuing the request manually from outside the cluster.
- The `NotifyNewConcerts` debug RPC's runbook describes how to call the RPC but does not describe how to verify delivery succeeded. The HTTP 200 response from the RPC means "the delivery loop ran"; per-subscription failures are recorded in the `RecordPushSend` metric and individual error log lines, not the RPC response.

Stakeholders: backend engineers (delivery correctness), platform engineers (network configuration), on-call rotation (debug ergonomics).

## Goals / Non-Goals

**Goals:**

- FCM Web Push delivery from any GKE pod (dev / staging / prod) reaches the FCM application layer (no longer blocked at the PGA VIP boundary).
- Outbound HTTP error responses preserve the upstream diagnostic body in structured logs by default — so the next "why is this failing" investigation reads the answer in one log line instead of replicating the request manually.
- The `NotifyNewConcerts` debug RPC's runbook makes the success criterion unambiguous: the RPC's HTTP status is necessary but not sufficient; per-subscription log lines and `RecordPushSend` metrics define delivery success.

**Non-Goals:**

- Adopting VPC Service Controls. Out of scope; this change explicitly de-scopes the restricted VIP because we are not using VPC-SC.
- Rotating the VAPID key pair. The existing pair is verified valid; rotation would force every browser to re-subscribe and is unnecessary.
- Changing the webpush library, payload encryption, or subscription model.
- Reducing Cloud NAT cost. Both VIPs (private and restricted) bypass Cloud NAT data-processing equally; no cost change is expected.
- Adding telemetry beyond the body capture. Tracing, metrics, and OTel attributes around webpush calls remain unchanged.

## Decisions

### D1. Switch `*.googleapis.com` from the restricted VIP to the private VIP

**Chosen:** Replace the wildcard CNAME target and the matching A record so DNS resolution returns `199.36.153.8/30` (private VIP) instead of `199.36.153.4/30` (restricted VIP). Single-zone structure (one `googleapis.com.` zone holding both records) is preserved.

**Rationale:** This is the canonical remediation in the GCP documentation for the failure mode "restricted VIP blocks a service we depend on." The private VIP supports the same `*.googleapis.com` wildcard, supports VMs without external IPs (the staging/prod scenario), and does not enforce a VPC-SC allowlist. We are not using VPC-SC, so the restricted VIP's filtering provided no security benefit and only caused outages.

**Alternatives considered:**

- *Keep restricted VIP, exclude `fcm.googleapis.com` from the private DNS zone via a more-specific record that points to public IPs.* Rejected: FCM has no stable public IP set we can hardcode; this would break whenever Google rotates IPs. Also fragile against new googleapis services we add later.
- *Keep restricted VIP, send FCM via Cloud NAT explicitly via a more-specific zone.* Same fragility plus depends on Cloud NAT egress, which staging/prod has but this couples FCM availability to NAT availability for no benefit.
- *Adopt VPC Service Controls so the restricted VIP makes sense.* Out of scope; would require designing a perimeter, integrating with Access Context Manager, and validating every cross-perimeter call site. Not justified by current security requirements.
- *Remove the private DNS zone entirely; rely on public DNS + Cloud NAT.* Loses the cost and security benefits of PGA (Cloud NAT data-processing fees in staging/prod, traffic leaving Google's backbone). Worse than switching VIPs.

**Risks:**

- The "supported via private VIP" guarantee is documented as "*most* Google APIs". Workspace services (Gmail, Docs) are explicitly excluded; FCM is not in the exclusion list. We mitigate by explicit dev validation via `curl` from inside the pod before promoting to staging/prod.
- Pulumi state still references the restricted VIP A record. The change is a same-resource update (record name change + IP change) which Pulumi will execute as a `replace` — there will be a brief moment of DNS unresolvability inside the VPC. Mitigated by Cloud DNS record TTL of 300s and the fact that dev nodes also have external IPs that fall through to public DNS (so dev is fail-tolerant during the change).

### D2. Capture error response body into apperr in the shared HTTP helper

**Chosen:** Modify `pkg/api/errors.go::FromHTTP` to optionally read up to 1024 bytes of the response body when the status is ≥ 400, and attach the captured bytes as a `slog.Attr` named `responseBody` on the resulting `apperr`. The cap of 1024 bytes is sufficient for typical Google edge errors (~500 bytes), FCM/MusicBrainz/Last.fm error JSON (~200 bytes), and is small enough to never blow up structured log payloads. Non-UTF-8 bytes are replaced with U+FFFD so the log entry stays valid.

**Rationale:** Centralizing the body read in the shared helper covers four call sites (Google Maps, fanart.tv main client, Last.fm, MusicBrainz) with a single change. The cap keeps log volume bounded. Non-printable byte handling preserves the structured log invariant.

**Alternatives considered:**

- *Log the body separately at the call sites instead of attaching to the error.* Loses the property that the body travels with the error to whichever boundary handles it; requires every caller to opt in. Rejected.
- *No cap; attach the full body.* Risks log payload bloat on large error responses. Rejected.
- *Capture at the connect-rpc interceptor level (apperr_connect).* Wrong layer — the interceptor sees connect errors after our infra has already mapped them, and many outbound HTTP errors never become connect errors (e.g., webpush delivery failures are swallowed inside the use case loop).

### D3. Webpush sender and logo fetcher get the same body capture

**Chosen:** `webpush/sender.go` and `fanarttv/logo_fetcher.go` do not use `FromHTTP` (they have their own status mapping). Apply the same body-read-and-attach logic inline in those two files. Code duplication is acceptable for the two cases because both have unique error-code mapping that doesn't fit the `FromHTTP` shape (webpush special-cases 410 → NotFound; logo fetcher special-cases 404 → nil-no-error).

**Alternatives considered:**

- *Refactor `FromHTTP` to accept a status-mapping function so both webpush and logo fetcher can use it.* Increases helper API surface area for two callers; the inline duplication is a few lines and clearer to read. Rejected for now.

### D4. Documented per-environment validation gate

**Chosen:** Tasks include explicit per-environment smoke tests before promotion. dev → staging → prod, each gated on a `curl` from inside the cluster + a `NotifyNewConcerts` RPC call that produces `RecordPushSend("success")` log entries.

**Rationale:** Although the documented Google behavior strongly implies success, the change touches network routing for every `*.googleapis.com` call from every pod (concert discovery, Cloud SQL connector, Secret Manager, Maps, Gemini, Logging, OTel, ...). A regression in any of those would be high-blast-radius. Per-environment validation catches it early.

### D5. Documentation update is part of the same change

**Chosen:** Extend `backend/docs/debug-rpc-notify-new-concerts.md` with a "How to verify delivery succeeded" section. Don't create a new spec for it — runbook is operational content.

**Rationale:** The 200-but-failing trap was a contributor to time-to-diagnose. Codifying the verification procedure now prevents the next person from making the same assumption. Docs-only change has no spec-level requirement.

## Risks / Trade-offs

- **[VIP switch is a same-resource replace in Pulumi]** → brief intra-VPC DNS unresolvability for `*.googleapis.com` during the apply. **Mitigation**: 300s TTL; staging/prod have higher real impact than dev — promote during low-traffic window if the metric volume warrants.
- **[private VIP is documented as supporting "most" googleapis services]** → some untested service path could fail post-switch. **Mitigation**: per-environment smoke gate; explicit pod-internal `curl` test against FCM (the worst-affected service) plus spot-checking Cloud SQL connector and Maps API calls.
- **[Body capture adds an extra read per error response]** → marginal latency increase on error path only. **Mitigation**: 1 KiB cap means a single small read; error path is by definition off the happy path; trade-off is overwhelmingly favorable for debugging.
- **[Code duplication between FromHTTP and the two custom clients]** → small technical debt. **Mitigation**: 2 sites only; refactor later if a third site appears.

## Migration Plan

1. cloud-provisioning PR: change DNS records in `network.ts`, update outdated comment about "PGA has no effect on dev nodes". Pulumi preview shows a `replace` on the two DNS records.
2. Backend PR: change `pkg/api/errors.go`, `webpush/sender.go`, `fanarttv/logo_fetcher.go`. Add unit tests for body capture (truncation, binary, empty, read-failure paths). Update runbook.
3. Order is deliberate: backend PR can land independently first (no infra dependency, immediate observability win that benefits everyone). cloud-provisioning PR follows.
4. After cloud-provisioning PR merges to main, Pulumi auto-deploys to dev. Run validation gate (D4). Once green, promote to staging via Pulumi Cloud console; run validation again; promote to prod.
5. **Rollback**: revert the cloud-provisioning PR commits. Pulumi auto-deploys the revert to dev. For staging/prod, manual Pulumi up of the prior state.

## Open Questions

- *Should `responseBody` be DEBUG-level instead of attached to error?* Currently spec says attach to apperr. Attaching keeps the body with the error wherever it travels (preferred). If structured log volume becomes an issue, we can revisit.
- *Should the body cap be configurable per call site?* Currently no — fixed 1 KiB. If a call site has structured JSON errors that consistently exceed 1 KiB, we can extend later.
