## 1. Pulumi: Replace Autopilot cluster with Standard cluster

- [x] 1.1 In `cloud-provisioning/src/gcp/components/kubernetes.ts`, replace the Autopilot cluster resource with a Standard zonal cluster in `asia-northeast2-a`
- [x] 1.2 Add a Spot node pool (`e2-standard-2`, `spot: true`, min 1 / max 4) to the new Standard cluster
- [x] 1.3 Set `enablePrivateNodes: false` in `privateClusterConfig` (public nodes)
- [x] 1.4 Remove or retain `masterIpv4CidrBlock` as appropriate (no longer required for public nodes)

## 2. Pulumi: Remove Cloud NAT and Cloud Router for dev

- [x] 2.1 In `cloud-provisioning/src/gcp/components/network.ts`, remove the `RouterNat` resource (`nat-osaka`) for dev
- [x] 2.2 Remove the `Router` resource (`nat-router-osaka`) for dev, or make it conditional on environment
- [x] 2.3 Verify no other resources depend on the Router/NAT before removal

## 3. Kubernetes: Update Spot nodeSelector in all dev overlays

- [x] 3.1 Find all `spot-nodeselector-patch.yaml` files under `k8s/namespaces/*/overlays/dev/`
- [x] 3.2 Replace `cloud.google.com/compute-class: autopilot-spot` with `cloud.google.com/gke-spot: "true"` in every file
- [x] 3.3 Verify the patch applies correctly via `kubectl kustomize k8s/namespaces/<namespace>/overlays/dev` for each namespace

## 4. Deploy and migrate workloads

- [x] 4.1 Run `pulumi preview` on the dev stack and confirm the plan: new Standard cluster created, old Autopilot cluster destroyed, Cloud NAT/Router removed
- [x] 4.2 Run `pulumi up` on the dev stack (downtime expected)
- [x] 4.3 Update local kubeconfig: `gcloud container clusters get-credentials <new-cluster> --zone asia-northeast2-a --project liverty-music-dev`
- [x] 4.4 Confirm ArgoCD syncs all applications automatically and all pods reach Running state
- [x] 4.5 Verify `kubectl get nodes -o wide` shows non-empty `EXTERNAL-IP` for all nodes

## 5. Verify cost reduction

- [x] 5.1 Confirm no Cloud NAT gateway exists: `gcloud compute routers nats list --router=nat-router-osaka --region=asia-northeast2 --project=liverty-music-dev` returns empty or error
- [x] 5.2 Confirm cluster is Standard: `gcloud container clusters describe <cluster> --zone asia-northeast2-a --format="value(autopilot.enabled)"` returns `False`
- [x] 5.3 Confirm Spot scheduling: `kubectl get pods -A -o jsonpath='{.items[*].spec.nodeSelector}'` includes `gke-spot: "true"` for all pods
