## REMOVED Requirements

### Requirement: Cloud NAT gateway for dev
**Reason**: Dev cluster nodes now have public external IPs (`enablePrivateNodes: false`), making Cloud NAT unnecessary for internet egress.
**Migration**: Remove the `RouterNat` and `Router` Pulumi resources scoped to the dev environment. No workload changes required — egress continues to work via node public IPs.
