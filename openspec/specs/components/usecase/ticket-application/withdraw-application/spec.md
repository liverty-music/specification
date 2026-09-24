# LotteryUseCase.WithdrawApplication

## Purpose

LotteryUseCase.WithdrawApplication lets a fan give up their own TicketApplication before the draw, releasing its hold.

## Requirements

### Requirement: Withdraw before the draw

WithdrawApplication SHALL take an application and the calling fan. It SHALL read the application with TicketApplication.Get, failing with NotFound when it does not exist; fail with PermissionDenied when the application belongs to another fan; and fail with FailedPrecondition when the application is not withdrawable. It SHALL then release the hold with TicketApplication.CancelAuthorization and only after that set the state to Withdrawn with TicketApplication.UpdateState. When the release fails, its error SHALL be returned and the application stays Applied. Withdrawal is possible until the draw runs, also after the window has closed.

#### Scenario: Withdraw before the draw

- **WHEN** a fan withdraws their Applied application
- **THEN** its hold is released and its state is Withdrawn, and the fan may apply again while the window is open

#### Scenario: Window closed but not drawn

- **WHEN** a fan withdraws an Applied application after the close time and before the draw
- **THEN** the hold is released and the application is Withdrawn

#### Scenario: Already drawn

- **WHEN** the application is Won or Lost
- **THEN** WithdrawApplication fails with FailedPrecondition and nothing changes

#### Scenario: Another fan's application

- **WHEN** a fan withdraws an application of another fan
- **THEN** WithdrawApplication fails with PermissionDenied and nothing changes

#### Scenario: Release fails

- **WHEN** TicketApplication.CancelAuthorization fails with Unavailable
- **THEN** WithdrawApplication fails with Unavailable and the application stays Applied
