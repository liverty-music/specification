## 1. Backend: Fix NATS Subscriber Configuration

- [x] 1.1 In `backend/internal/infrastructure/messaging/subscriber.go`, remove `AckAsync: true` from `JetStreamConfig`
- [x] 1.2 In the same file, replace `nats.DeliverAll()` with `nats.DeliverNew()` in `SubscribeOptions`

## 2. Verification

- [x] 2.1 Run `make check` in `backend/` to confirm lint and tests pass
- [x] 2.2 Open a PR to backend and confirm CI passes
