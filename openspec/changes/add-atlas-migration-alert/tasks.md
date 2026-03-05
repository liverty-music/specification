## 1. Add Atlas Migration Alert Policy

- [ ] 1.1 Add `gcp.monitoring.AlertPolicy` for Atlas Operator migration failures in `monitoring.ts`
- [ ] 1.2 Use log filter: `resource.type="k8s_container"`, `namespace_name="atlas-operator"`, `container_name="manager"`, `textPayload=~"TransientErr|BackoffLimitExceeded"`
- [ ] 1.3 Use same notification channels, rate limit (12h), and auto-close (1h) as existing workload alerts
- [ ] 1.4 Add documentation/triage steps specific to Atlas migration failures

## 2. Deploy and Verify

- [ ] 2.1 Run `pulumi preview` to verify the new alert policy resource
- [ ] 2.2 Deploy with `pulumi up` after user approval
