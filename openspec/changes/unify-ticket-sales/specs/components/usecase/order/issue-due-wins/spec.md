# Spec Delta

## MODIFIED Requirements

### Requirement: Issue within one minute after the draw

IssueDueWins SHALL run every 1 minute. It SHALL list the Won LotteryEntries without an Order with Order.ListLotteryEntryIDsAwaitingIssuance and run IssuanceUseCase.IssueFromCapturedWin for each. An entry whose issuance fails SHALL NOT stop the others and is tried again on the next run, without limit. When the listing fails, IssueDueWins SHALL fail with that error and issue nothing.

#### Scenario: Won application
- **WHEN** a draw records an entry Won
- **THEN** its Order and Tickets are issued within 1 minute

#### Scenario: Issuance fails
- **WHEN** issuance of one entry fails
- **THEN** the other entries are still issued and the failed one is tried again 1 minute later
