# components/usecase/user/update Specification

## Purpose
UserUseCase.Update lets a fan change their own full name and phone number, the 本人確認 details shown on the face of their tickets, at any time.

## Requirements

### Requirement: The caller changes their own personal details

Update SHALL take the calling fan and a new full name, a new phone number or both. It SHALL resolve the caller as UserUseCase.ResolveCaller does, with the same failures; fail with InvalidArgument when a given value breaks the User's personal details rule; store the values with User.UpdatePersonalDetails, keeping a value that was not given; and return the User. The faces of the fan's Tickets SHALL show the new values from then on.

#### Scenario: Fan corrects their name
- **WHEN** a fan who entered as 山田 花子 updates the full name to 佐藤 花子
- **THEN** the User carries 佐藤 花子 and the faces of the fan's Tickets show 佐藤 花子

#### Scenario: Only the phone number given
- **WHEN** the fan gives only a new phone number
- **THEN** the phone number changes and the full name stays

#### Scenario: Invalid phone number
- **WHEN** the new phone number is not in E.164 form
- **THEN** Update fails with InvalidArgument and nothing changes
