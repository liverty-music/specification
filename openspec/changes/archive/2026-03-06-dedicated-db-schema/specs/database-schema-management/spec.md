## ADDED Requirements

### Requirement: The system MUST manage PostgreSQL schemas declaratively via Pulumi

The infrastructure SHALL use the `@pulumi/postgresql` provider to create and manage PostgreSQL schemas and permissions. The provider SHALL connect to Cloud SQL via Private Service Connect within the VPC during `pulumi up`.

#### Scenario: Schema creation on first deployment

- **WHEN** `pulumi up` is executed with PSC connectivity to Cloud SQL
- **THEN** an `app` schema SHALL be created in the database
- **AND** the schema SHALL be managed as a Pulumi resource with state tracking

#### Scenario: Schema already exists

- **WHEN** `pulumi up` is executed and the `app` schema already exists
- **THEN** no changes SHALL be applied to the schema
- **AND** Pulumi SHALL report no diff for the schema resource

### Requirement: The system MUST grant schema permissions to the backend IAM service account

The infrastructure SHALL grant `CREATE` and `USAGE` privileges on the `app` schema to the backend application's IAM service account. Default privileges SHALL ensure the IAM user has full access to tables and sequences created in the schema.

#### Scenario: IAM user can create tables in the schema

- **WHEN** the backend IAM service account connects to Cloud SQL
- **AND** the `search_path` is set to `app,public`
- **THEN** the service account SHALL be able to create tables in the `app` schema
- **AND** the service account SHALL be able to read and write data in those tables

#### Scenario: Default privileges apply to future objects

- **WHEN** new tables or sequences are created in the `app` schema by any owner
- **THEN** the backend IAM service account SHALL automatically have full privileges on those objects
