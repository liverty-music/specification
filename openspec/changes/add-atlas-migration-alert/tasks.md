## 1. Add Atlas Migration Alert Policy

- [x] 1.0 Verify Atlas Operator log structure in Cloud Logging: determine whether logs use `textPayload` or `jsonPayload`, and identify the exact field containing `TransientErr`/`BackoffLimitExceeded` keywords
- [x] 1.1 Add `gcp.monitoring.AlertPolicy` for Atlas Operator migration failures in `monitoring.ts`
- [x] 1.2 Use log filter: `resource.type="k8s_container"`, `namespace_name="atlas-operator"`, `container_name="manager"`, and the verified `textPayload` field matching `TransientErr|BackoffLimitExceeded`
- [x] 1.3 Use same notification channels, rate limit (12h), and auto-close (1h) as existing workload alerts
- [x] 1.4 Add documentation/triage steps specific to Atlas migration failures

## 2. Deploy and Verify

- [x] 2.1 Run `pulumi preview` to verify the new alert policy resource
- [ ] 2.2 Deploy with `pulumi up` after user approval
