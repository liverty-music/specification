# IssuanceUseCase.IssueDueWins

## Purpose

IssuanceUseCase.IssueDueWins issues an Order and tickets for every Won TicketApplication that has none yet.

## Requirements

### Requirement: Issue within one minute after the draw

IssueDueWins SHALL run every 1 minute. It SHALL list the Won applications without an Order with Order.ListApplicationIDsAwaitingIssuance and run IssuanceUseCase.IssueFromCapturedWin for each. An application whose issuance fails SHALL NOT stop the others and is tried again on the next run, without limit. When the listing fails, IssueDueWins SHALL fail with that error and issue nothing.

#### Scenario: Won application

- **WHEN** a draw records an application Won
- **THEN** its Order and Tickets are issued within 1 minute

#### Scenario: Issuance fails

- **WHEN** issuance of one application fails
- **THEN** the other applications are still issued and the failed one is tried again 1 minute later
