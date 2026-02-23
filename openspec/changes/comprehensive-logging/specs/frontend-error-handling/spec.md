## MODIFIED Requirements

### Requirement: Service Error Recovery Patterns
The system SHALL replace silent error swallowing in services with explicit error states that callers can distinguish from empty-data states.

#### Scenario: Service method returns error result instead of empty fallback
- **WHEN** a service method fails to fetch data from the backend
- **THEN** the method SHALL throw the error to the caller (not silently return an empty array or false)
- **AND** the caller SHALL handle the error via `promise.bind` catch block or explicit try/catch with user feedback

#### Scenario: Fire-and-forget operations retry once and provide user feedback on failure
- **WHEN** a fire-and-forget RPC operation (e.g., artist unfollow, passion level update) fails
- **THEN** the system SHALL immediately retry the operation once
- **AND** if the retry also fails, the system SHALL display a toast notification via `IToastService` informing the user of the failure
- **AND** the system SHALL revert any optimistic UI updates
- **AND** the system SHALL log the failure at ERROR level with operation details

#### Scenario: Fire-and-forget retry succeeds
- **WHEN** a fire-and-forget RPC operation fails on the first attempt but succeeds on retry
- **THEN** the system SHALL log the initial failure at WARN level with message "RPC failed, retrying"
- **AND** the system SHALL NOT display a toast notification to the user
- **AND** the system SHALL NOT revert any optimistic UI updates
