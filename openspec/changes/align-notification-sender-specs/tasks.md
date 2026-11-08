## 1. Specification

- [x] 1.1 Add the `lottery_loss, concert cancelled` row to the copy table of `components/entity/notification`, with the headline and detail in `copyLotteryCancelled` of `backend` `internal/entity/notification_message.go` on `main`. Verify: the row's four texts equal the backend's ja and en strings.
- [x] 1.2 Replace the description of the pushed text in `send-lottery-loss` and `send-order-refunded` with a pointer to the entity's rendering. Verify: neither requirement's text describes the pushed wording; only the scenarios name what the fan reads.
- [x] 1.3 Edit the Purpose of `components/usecase/user/create` in the main spec so the preferred language is required and the home area optional. Verify: the Purpose matches the requirement "Create SHALL take ... preferred language and, optionally, a Home".
- [x] 1.4 Run `openspec validate align-notification-sender-specs --strict` and `python3 scripts/check-scenario-coverage.py align-notification-sender-specs`. Verify: both pass.
