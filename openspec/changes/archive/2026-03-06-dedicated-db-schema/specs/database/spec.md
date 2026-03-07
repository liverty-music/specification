## MODIFIED Requirements

### Requirement: The system MUST provide persistent relational storage

The system SHALL provide a durable, consistent store for relational data using a dedicated PostgreSQL schema.

#### Scenario: Production Deployment

Given the backend service is deployed to production
When it attempts to persist user data
Then the data SHALL be stored in a highly available Cloud SQL instance
And the data SHALL be encrypted at rest
And the data SHALL reside in a dedicated `app` schema, not the default `public` schema
