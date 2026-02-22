## ADDED Requirements

### Requirement: The system MUST manage PostgreSQL schemas declaratively via Pulumi

The infrastructure SHALL use the `@pulumi/postgresql` provider to create and manage PostgreSQL schemas and permissions. The provider SHALL connect to Cloud SQL via Cloud SQL Auth Proxy running locally during `pulumi up`.

#### Scenario: Schema creation on first deployment

- **WHEN** `pulumi up` is executed with Cloud SQL Auth Proxy running
- **THEN** a `liverty_music` schema SHALL be created in the `backend-app` database
- **AND** the schema SHALL be managed as a Pulumi resource with state tracking

#### Scenario: Schema already exists

- **WHEN** `pulumi up` is executed and the `liverty_music` schema already exists
- **THEN** no changes SHALL be applied to the schema
- **AND** Pulumi SHALL report no diff for the schema resource

### Requirement: The system MUST grant schema permissions to the backend IAM service account

The infrastructure SHALL grant `CREATE` and `USAGE` privileges on the `liverty_music` schema to the backend application's IAM service account. Default privileges SHALL ensure the IAM user has full access to tables and sequences created in the schema.

#### Scenario: IAM user can create tables in the schema

- **WHEN** the backend IAM service account connects to Cloud SQL
- **AND** the `search_path` is set to `liverty_music`
- **THEN** the service account SHALL be able to create tables in the `liverty_music` schema
- **AND** the service account SHALL be able to read and write data in those tables

#### Scenario: Default privileges apply to future objects

- **WHEN** new tables or sequences are created in the `liverty_music` schema by any owner
- **THEN** the backend IAM service account SHALL automatically have full privileges on those objects
