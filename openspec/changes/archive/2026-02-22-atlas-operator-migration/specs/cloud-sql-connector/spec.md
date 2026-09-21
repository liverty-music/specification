## REMOVED Requirements

### Requirement: The system MUST provide a standard sql.DB connection for migrations

**Reason**: Migrations are no longer executed by the application. The Atlas Kubernetes Operator handles migration execution using its own database connection as the `postgres` user.

**Migration**: Remove `NewMigrationDB()` and related goose integration from the `rdb` package. The Atlas Operator manages migration connectivity independently.
