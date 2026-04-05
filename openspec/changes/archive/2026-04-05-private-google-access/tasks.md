## 1. Add private DNS zones in Pulumi

- [x] 1.1 In `cloud-provisioning/src/gcp/components/network.ts`, add a private `ManagedZone` for `googleapis.com.` bound to the VPC (`vpc-osaka`)
- [x] 1.2 Add a wildcard CNAME `RecordSet` `*.googleapis.com.` → `restricted.googleapis.com.` in the `googleapis.com` zone
- [x] 1.3 ~~Add a private `ManagedZone` for `restricted.googleapis.com.` bound to the VPC~~ — **Superseded by PR #188**: original two-zone plan failed because Cloud DNS private zones do not follow cross-zone CNAMEs. No separate `restricted.googleapis.com.` zone was created.
- [x] 1.4 Add an A `RecordSet` for `restricted.googleapis.com.` with all four IPs (199.36.153.4–7) — placed in the **same `googleapis.com.` zone** (not a separate zone, corrected in PR #188)

## 2. Deploy

- [x] 2.1 Run `pulumi preview` on the dev stack and confirm only DNS resources are added — no compute or network changes (note: final architecture has 1 zone + 2 record sets, not 2 zones)
- [x] 2.2 Run `pulumi up` on the dev stack
- [x] 2.3 Repeat `pulumi preview` + `pulumi up` for staging and prod stacks

## 3. Verify

- [x] 3.1 From a running pod, verify DNS resolution: `kubectl exec -n backend deploy/server-app -- nslookup storage.googleapis.com` — response IPs must be in 199.36.153.4–7
- [x] 3.2 Verify Logging/Monitoring still works after DNS change (check Cloud Logging for recent entries from backend pods)
- [x] 3.3 For staging/prod: confirm Cloud NAT data processing metrics show reduced bytes after rollout
