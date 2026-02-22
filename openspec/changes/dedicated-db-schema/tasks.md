## 1. Pulumi Infrastructure (cloud-provisioning)

- [ ] 1.1 Install `@pulumi/postgresql` provider (`npm install @pulumi/postgresql`)
- [ ] 1.2 Add postgresql provider, schema, grants, and default privileges to `src/gcp/components/postgres.ts`
- [ ] 1.3 Add `DATABASE_SCHEMA=liverty_music` to `k8s/namespaces/backend/base/server/configmap.env`
- [ ] 1.4 Run `kubectl kustomize` dry-run to verify K8s manifests

## 2. Backend Config (backend)

- [ ] 2.1 Add `Schema` field to `DatabaseConfig` in `pkg/config/config.go` with `DATABASE_SCHEMA` env var and `public` default
- [ ] 2.2 Update `GetDSN()` to include `search_path` parameter
- [ ] 2.3 Update `atlas.hcl` dev database URL to use `search_path=liverty_music`

## 3. Deploy and Verify

- [ ] 3.1 Start Cloud SQL Auth Proxy locally
- [ ] 3.2 Run `pulumi preview` then `pulumi up` to create schema and grants
- [ ] 3.3 Verify schema exists via `psql \dn`
- [ ] 3.4 Restart backend pod and confirm migration logs show 17 tables applied
- [ ] 3.5 Verify API calls return 200 instead of 500
