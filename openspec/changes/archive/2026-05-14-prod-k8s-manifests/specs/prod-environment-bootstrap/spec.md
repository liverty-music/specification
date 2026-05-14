## REMOVED Requirements

### Requirement: Prod GCP infrastructure ships without ArgoCD bootstrap (workloads in follow-up change)
**Reason**: The follow-up `prod-k8s-manifests` change (this one) authors the ArgoCD bootstrap and per-namespace prod overlays. The "ships without ArgoCD bootstrap" disclaimer is therefore obsolete — after this change, prod ships *with* the full manifest set.

**Migration**: Replaced by the new requirement "Prod cluster SHALL run a full ArgoCD Application set matching dev's structure" in the new `prod-k8s-manifests` capability spec. Operators no longer need to read the prod cluster as a "GCP-only" deliverable; the cluster is now fully manifest-managed via ArgoCD from this change forward.
