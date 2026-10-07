# Spec Delta

## MODIFIED Requirements

### Requirement: Lottery requests are validated at the boundary

Every lottery call SHALL fail with InvalidArgument, before any usecase runs, when no phase is given. CreateAuthorization and Apply SHALL fail with InvalidArgument when the requested ticket count is not greater than 0; Apply SHALL also fail with InvalidArgument when the applicant's identity details or the card authorization are missing, or when the applicant identity breaks the TicketApplication identity rule, including a phone number that is not in E.164 form.

#### Scenario: Zero tickets

- **WHEN** Apply is called with a requested ticket count of 0
- **THEN** it fails with InvalidArgument and nothing is applied

#### Scenario: Domestic-format phone number

- **WHEN** Apply is called with the applicant phone number `090-1234-5678`
- **THEN** it fails with InvalidArgument and nothing is applied

#### Scenario: E.164 phone number

- **WHEN** Apply is called with the applicant phone number `+819012345678` and every other field valid
- **THEN** the request passes the boundary and LotteryUseCase.Apply runs
