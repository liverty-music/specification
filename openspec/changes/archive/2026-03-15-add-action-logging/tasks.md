## 1. Implementation

- [x] 1.1 Add `require("zitadel/log")` and logging to `cloud-provisioning/src/zitadel/scripts/add-email-claim.js`
- [x] 1.2 Run `make check` in cloud-provisioning to verify linting passes

## 2. Deploy & Verify

- [x] 2.1 Run `pulumi preview` to confirm only the Action script resource changes
- [x] 2.2 Run `pulumi up` to deploy the updated Action to Zitadel Cloud (requires user approval)
- [x] 2.3 Trigger a signup flow and check Zitadel Console Events for Action logs
