## 1. cloud-provisioning: sign-in service resources

- [ ] 1.1 In Pulumi, add an API application with private-key JWT and an application key to the product and admin-console projects, switch the organizer-console `backend-api` application to private-key JWT with a key, store the three keys in Secret Manager with ESO-only access, export the product and admin-console project ids, and correct the `fan-passkey-recovery` description; verify the prod preview in the PR shows only these changes, merge
- [ ] 1.2 Owner: run the prod `pulumi up` from the Pulumi Cloud console; verify read-only that the three secrets have a version

## 2. measurement

- [ ] 2.1 Through a port-forward to `zitadel-api` with the two host headers, introspect a test account's access token and ID token for each audience, fetch a token and the keys, and make one read-only gRPC call (get the test account's identity); then sign up a throwaway fan account, delete it in the app and introspect its still unexpired access token. Verify the access token is active, the ID token and the removed account's token are not, the gRPC call resolves the instance, and record the p50 and p95 of 100 introspections in design.md. Stop and ask when any expectation fails or p95 exceeds 300 ms

## 3. cloud-provisioning: manifests

- [ ] 3.1 Add the internal sign-in service URL to the API and identity workloads, the project ids and the key mounts (ExternalSecret per API) to the three APIs, rename the identity Service and container port to `workflow-worker`, and add the signed-in call outage to `docs/runbooks/zitadel-hang.md`; verify both overlays render and, after merge, read-only that the secrets sync and the pods are ready

## 4. backend: internal calls (design "Cluster-internal calls")

- [ ] 4.1 Send every sign-in service call (keys, token, gRPC) to the internal URL with the host headers, require the setting outside local, and rename `IDENTITY_EVENT_CONSUMER_PORT`; verify tests that each client dials the internal address with both headers while issuer and assertion audience stay public, and that a missing setting stops the process

## 5. backend: sign-in (components/adapter/*/api/rpc/sign-in, identity-provider-credentials)

- [ ] 5.1 Add the introspection client with its 60-second cache, latency and hit metrics, and Unavailable on failure; verify unit tests for "Calls within a minute", "Sign-in service unreachable", "Sign-in service not answering" and "Expired token", and that the reuse is counted from the ask
- [ ] 5.2 Check audience then activity in the fan, admin console and organizer authentication, keeping the codes; verify one test per scenario of the three `sign-in` specs
- [ ] 5.3 Verify configuration tests that each API requires its own key and project id, and no other process is given one ("API server deployment", "Signed-in calls keep working")

## 6. backend: forgetting removed identities (components/entity/user, components/usecase/user/delete)

- [ ] 6.1 Add `User.ForgetRemovedIdentity`; verify one repository test per scenario of `entity/user/forget-removed-identity` and the modified scenarios of `entity/user/create` and `entity/user/delete`
- [ ] 6.2 Start the delayed `forget-removed-identity` workflow from `delete-user` under a patch and register it; verify one test per scenario of "A removed identity is forgotten"
- [ ] 6.3 Open the backend PR, merge, release; confirm read-only in prod: rollout, signed-in calls of each app succeed, no key fetch from a node public IP at the load balancer, introspection p95 within 300 ms, `deleted_user_identities` holds no row older than the release (report any), and no `workflow.needs_admin` for the new workflow

## 7. production behavior

- [ ] 7.1 With a test account, send its ID token and another app's access token to each API; verify Unauthenticated and PermissionDenied, and that the apps' own calls succeed
