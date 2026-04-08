## 1. Right-size CPU requests — backend

- [x] 1.1 In `k8s/namespaces/backend/overlays/dev/kustomization.yaml`, reduce `server-app` CPU request from 50m to 10m (memory stays at 60Mi)
- [x] 1.2 In `k8s/namespaces/backend/overlays/dev/kustomization.yaml`, reduce `consumer-app` CPU request from 50m to 10m (memory stays at 20Mi)
- [x] 1.3 In `k8s/namespaces/backend/overlays/dev/kustomization.yaml`, patch the consumer-app ScaledObject to set `maxReplicaCount: 1`

## 2. Right-size CPU requests — frontend

- [x] 2.1 In `k8s/namespaces/frontend/overlays/dev/kustomization.yaml`, reduce `caddy` CPU request from 50m to 10m

## 3. Right-size CPU requests — ArgoCD

- [x] 3.1 In `k8s/namespaces/argocd/overlays/dev/kustomization.yaml`, add a patch for `argocd-application-controller`: CPU request 20m, memory request 320Mi
- [x] 3.2 In `k8s/namespaces/argocd/overlays/dev/kustomization.yaml`, add patches for `argocd-repo-server`, `argocd-server`, and `argocd-applicationset-controller`: CPU request 10m each
- [x] 3.3 In `k8s/namespaces/argocd/overlays/dev/kustomization.yaml`, add patches for `argocd-redis` and `argocd-redis-secret-init`: CPU request 10m each

## 4. Right-size CPU requests — KEDA

- [x] 4.1 In `k8s/namespaces/keda/overlays/dev/values.yaml`, set operator CPU request to 10m
- [x] 4.2 In `k8s/namespaces/keda/overlays/dev/values.yaml`, set metricServer CPU request to 10m
- [x] 4.3 In `k8s/namespaces/keda/overlays/dev/values.yaml`, set webhooks CPU request to 10m

## 5. Right-size CPU requests — NATS

- [x] 5.1 In `k8s/namespaces/nats/overlays/dev/values.yaml`, reduce the container merge CPU request from 50m to 10m

## 6. Right-size CPU requests — OTel Collector

- [x] 6.1 In `k8s/namespaces/otel-collector/overlays/dev/kustomization.yaml`, reduce collector CPU request from 50m to 10m

## 7. Right-size CPU requests — External Secrets

- [x] 7.1 In `k8s/namespaces/external-secrets/overlays/dev/`, reduce controller CPU request to 10m
- [x] 7.2 In `k8s/namespaces/external-secrets/overlays/dev/`, reduce webhook CPU request to 10m
- [x] 7.3 In `k8s/namespaces/external-secrets/overlays/dev/`, reduce cert-controller CPU request to 10m

## 8. Right-size CPU requests — Atlas Operator

- [x] 8.1 In `k8s/namespaces/atlas-operator/overlays/dev/`, add a CPU request patch: 10m

## 9. Right-size CPU requests — Reloader

- [x] 9.1 In `k8s/namespaces/reloader/overlays/dev/kustomization.yaml`, add a CPU request patch for the reloader Deployment: 10m

## 10. Validate Kubernetes manifests

- [x] 10.1 Run `kubectl kustomize k8s/namespaces/backend/overlays/dev` and verify no errors, spot nodeSelector present, consumer ScaledObject maxReplicaCount=1
- [x] 10.2 Run `kubectl kustomize k8s/namespaces/argocd/overlays/dev` and verify all argocd components have correct CPU requests
- [x] 10.3 Run `make lint-k8s` and confirm all kube-linter checks pass with no spot nodeSelector warnings

## 11. Update Pulumi cluster definition

- [x] 11.1 In `src/gcp/components/kubernetes.ts`, remove `datapathProvider: 'ADVANCED_DATAPATH'` from the dev cluster definition
- [x] 11.2 In `src/gcp/components/kubernetes.ts`, add `loggingConfig: { enableComponents: ['SYSTEM_COMPONENTS'] }` to the dev cluster
- [x] 11.3 In `src/gcp/components/kubernetes.ts`, add `monitoringConfig: { enableComponents: ['SYSTEM_COMPONENTS'], managedPrometheus: { enabled: false } }` to the dev cluster
- [x] 11.4 In `src/gcp/components/kubernetes.ts`, change dev node pool `machineType` from `e2-standard-2` to `e2-medium`
- [x] 11.5 In `src/gcp/components/kubernetes.ts`, change dev node pool `maxNodeCount` from 4 to 2

## 12. Validate Pulumi and open PR

- [x] 12.1 Run `make lint-ts` in cloud-provisioning and fix any TypeScript or biome errors
- [x] 12.2 Run `pulumi preview` (dev stack) and review the diff — confirm cluster replacement is expected and note any destructive operations
- [ ] 12.3 Open PR to cloud-provisioning `main`; wait for CI to pass
- [ ] 12.4 Merge PR (Pulumi Cloud Deployments will trigger `pulumi up` automatically for dev)
- [ ] 12.5 Monitor cluster recreation in Pulumi Cloud console and verify all ArgoCD apps reach Synced/Healthy state after recreation
