## 1. Pulumi Infrastructure (cloud-provisioning)

- [x] 1.1 Install `@pulumi/postgresql` provider (`npm install @pulumi/postgresql`)
- [x] 1.2 Add postgresql provider, schema, grants, and default privileges to `src/gcp/components/postgres.ts`
- [x] 1.3 Add `DATABASE_SCHEMA=app` to K8s ConfigMaps for all workloads (server, consumer, cronjob)
- [x] 1.4 Run `kubectl kustomize` dry-run to verify K8s manifests

## 2. Backend Config (backend)

- [x] 2.1 Add `Schema` field to `DatabaseConfig` in `pkg/config/config.go` with `DATABASE_SCHEMA` env var and `app` default
- [x] 2.2 Update `GetDSN()` to include `search_path=<schema>,public` parameter
- [x] 2.3 Update `atlas.hcl` dev URL to include `search_path=app,public`

## 3. Deploy and Verify

- [x] 3.1 Run `pulumi preview` then `pulumi up` to create schema and grants (requires PSC connectivity to Cloud SQL)
- [x] 3.2 Verify schema exists via Cloud SQL Studio or `kubectl exec` into a pod with `psql`
- [x] 3.3 Trigger AtlasMigration and confirm logs show 13 tables applied in `app` schema
- [x] 3.4 Verify API calls return 200 instead of 500
