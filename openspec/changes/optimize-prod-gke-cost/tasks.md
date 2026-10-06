## 1. Kubernetes hygiene (cloud-provisioning, no ComputeClass dependency; D3, D4, D5, D7)

- [ ] 1.1 Set `fan-api`, `fan-web-app` and `zitadel-api` to 1 replica in their prod overlays and remove their hostname `topologySpreadConstraints`; leave a comment with the launch-time restore (2 replicas, `ScheduleAnyway`, `nodeTaintsPolicy: Honor`, `minAvailable: 1`). Verify `kubectl kustomize` of each prod overlay shows `replicas: 1` and no spread
- [ ] 1.2 Remove PDBs on single-replica workloads and disable the broken `zitadel-api-login` PDB in the zitadel values; keep the NATS PDB. Verify the rendered output has no PDB for those workloads and, after sync, `kubectl get pdb -A` shows no `ALLOWED DISRUPTIONS 0` outside NATS
- [ ] 1.3 Add explicit `ephemeral-storage` requests and equal limits to every container and init container in prod (100Mi default; argocd repo-server and zitadel sized from measured `emptyDir`/cache usage). Verify the rendered manifests leave no container without the request, and after sync the live Pod specs show those values instead of 1Gi
- [ ] 1.4 Remove `cloud-sql-proxy` from `k8s/namespaces/backend/overlays/prod` (keep the `backend-app` KSA; dev untouched). Verify the prod render has no proxy Deployment and the dev render is unchanged
- [ ] 1.5 Set `webhook.create: false` and `certController.create: false` in `k8s/namespaces/external-secrets/base/values.yaml` and drop the now-targetless patches in the dev and prod overlays. Verify the render has no ValidatingWebhookConfiguration or cert-controller, and after sync every ExternalSecret stays `SecretSynced` in dev and prod
- [ ] 1.6 Add comments stating the purpose of `reloader`, `argocd-server`, KEDA and the other support components next to their prod settings. Verify they are in the diff
- [ ] 1.7 Require Spot for the atlas `backend-migration-atlas-dev-db` Pod and set `ttlSecondsAfterFinished: 86400` on every CronJob `jobTemplate`. Verify both in the render, and after sync the next migration plan's dev-db Pod runs on a Spot node
- [ ] 1.8 Follow `k8s/CLAUDE.md` dry-run and cost checks, open the PR, merge it after green CI, and verify every ArgoCD Application is `Synced/Healthy` in prod and dev

## 2. ComputeClass verification V1 (manual, scratch namespace; D9)

- [ ] 2.1 Create a scratch namespace and a throwaway non-default ComputeClass with only an on-demand `podFamily: general-purpose` rule. Start a 50m test Deployment on it and verify it runs on a non-Spot node
- [ ] 2.2 Patch the class to Spot-first + on-demand with `activeMigration.optimizeRulePriority: true` and `whenUnsatisfiable: ScaleUpAnyway`. Verify the API accepts it, a Spot node appears, the Pod moves to a node labelled `cloud.google.com/gke-spot=true`, and the Pod requests show the non-default 0.5 vCPU minimum. Record the results (commands and output) in the PR description of group 3
- [ ] 2.3 Delete the scratch namespace and class. If 2.2 failed, stop here and follow the D9 fallback (required Spot for every workload) instead of groups 3–5

## 3. Pulumi changes (cloud-provisioning `src/gcp/`; D1, D6, D8)

- [ ] 3.1 Set `clusterAutoscaling.defaultComputeClassEnabled: true` on the prod cluster. Verify `pulumi preview` shows an in-place update, not a replace
- [ ] 3.2 Turn off proactive capacity provisioning (`no-performance`): confirm the provider field. If one exists, set it in Pulumi; if not, apply it with gcloud and record the command in a runbook. Verify the cluster describe output reflects it and, within a day, no `gke-system-balloon-pod` remains
- [ ] 3.3 Stop creating `api-gateway-static-ip` in dev (keep it where the gateway uses it). Verify the dev preview deletes only that address and no gateway resource references it
- [ ] 3.4 Add Artifact Registry cleanup policies in dev and prod, first with `cleanupPolicyDryRun: true`. Choose the keep count and age from rollback needs (the open question in design.md). Verify that after a day the dry-run log lists only old versions and no image currently deployed, then turn off dry-run
- [ ] 3.5 Set the Cloud SQL `diskAutoresizeLimit` and the KMS etcd key rotation to 365 days. Verify both in the preview as in-place updates
- [ ] 3.6 Open the PR and merge it after green CI and a clean preview (dev applies automatically); the user runs the prod `pulumi up`. Verify that `gcloud container clusters describe` shows the default ComputeClass setting enabled

## 4. Default ComputeClass and staged move (cloud-provisioning `k8s/`; D1, D2, D9 V2–V4)

- [ ] 4.1 Add the `default` ComputeClass to `k8s/cluster/`. Verify `kubectl get computeclass default` reports it as healthy and no existing Pod restarted (V2)
- [ ] 4.2 Drop the Spot patch from `organizer-console-web-app` only. Verify the new Pod runs on a Spot node, has the Spot toleration, and its live requests remain 50m / 52Mi (V3). If the minimum rose, revert and stop
- [ ] 4.3 Drop the Spot patches and selectors namespace by namespace: frontend, backend (Deployments and CronJobs), zitadel (including hook Jobs), external-secrets, keda, otel-collector, reloader, atlas-operator, then argocd last. Keep NATS's explicit `cloud.google.com/gke-spot: "true"` nodeSelector. Verify after each sync that the namespace's Pods are on Spot nodes and `Healthy`
- [ ] 4.4 System check: confirm all user Pods except NATS have no Spot selector and run on Spot nodes, and that the next day's billing export shows on-demand Pod CPU close to 0

## 5. NATS PVC (cloud-provisioning `k8s/namespaces/nats`; D8)

- [ ] 5.1 Change the NATS volume claim template to `standard-rwo` and re-create the StatefulSet and PVC in a quiet window. Verify that the new PVC is `standard-rwo`, NATS is `Healthy`, NACK re-creates the streams and consumers, and the backend consumers reconnect (no consumer-lag alert)

## 6. Cost check

- [ ] 6.1 Two weeks after group 4, compare the billing export with the estimates in proposal.md (Kubernetes about ¥3,000/month; non-Kubernetes about ¥1,600–1,900/month less). Record the result in the change before archiving
