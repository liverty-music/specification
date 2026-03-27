## 1. Update Pulumi Branch Protection Config

- [x] 1.1 In `cloud-provisioning/src/index.ts`, set frontend `requiredStatusCheckContexts` to `['CI Success']`
- [x] 1.2 In `cloud-provisioning/src/index.ts`, set cloud-provisioning `requiredStatusCheckContexts` to `['CI Success']`

## 2. Verify & Deploy

- [x] 2.1 Run `make check` in cloud-provisioning to ensure lint passes
- [x] 2.2 Run `pulumi preview -s prod` to verify the branch protection changes
- [x] 2.3 Run `pulumi up -s prod` to apply (requires user approval)

## 3. Validate

- [x] 3.1 Verified frontend branch protection: `CI Success` required (confirmed via GitHub API)
- [x] 3.2 Verified cloud-provisioning branch protection: `CI Success` required + strict mode (confirmed via GitHub API)
