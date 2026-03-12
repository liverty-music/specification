## 1. IAM Role Addition

- [x] 1.1 Add `roles/serviceusage.serviceUsageConsumer` to backend-app SA role bindings in `cloud-provisioning/src/gcp/components/kubernetes.ts`
- [x] 1.2 Run `make check` in cloud-provisioning to verify lint and type checks pass

## 2. Deployment

- [x] 2.1 Run `pulumi preview` on dev stack to verify the IAM binding diff
- [x] 2.2 Run `pulumi up` on dev stack after user approval
- [x] 2.3 Verify Places API calls succeed by checking consumer logs for successful venue enrichment (no more 403)
