## 1. Events carry the trace (backend, components/infrastructure/backend/process/trace-propagation)

- [x] 1.1 Add `traceContextPublisher` in `internal/infrastructure/messaging` that injects the message context into `msg.Metadata` with the global propagator, and wrap it inside `wotel.NewPublisherDecorator` for both the NATS and the GoChannel publisher in `publisher.go`; verify with a unit test that a published message carries `traceparent` whose parent span id is the producer span, not the caller span
- [x] 1.2 Add the `extractTraceContext` router middleware and register it right before `wotel.Trace()` in `router.go`, and rewrite the comment at `router.go:50` to say what the two middlewares do; verify with `go test ./internal/infrastructure/messaging/...`
- [x] 1.3 Add router tests on a GoChannel pub/sub with an in-memory span recorder, annotated `// @spec components/infrastructure/backend/process/trace-propagation "<scenario>"`, covering "Consumer continues the publisher's trace", "Two hops", "Event without trace context" and "Redelivered event" (handler fails once, retry middleware runs it again); verify they pass

## 2. Jobs record traces (backend, components/infrastructure/backend/process/trace-propagation)

- [x] 2.1 Add `telemetry.StartJobRun` and `telemetry.StartJobItem` (new root plus a link to the run span) in `pkg/telemetry`, with unit tests on an in-memory span recorder that the item span has a new trace id and one link to the run span; verify they pass
- [x] 2.2 Start a run span and one item span per artist in `cmd/job/concert-discovery/main.go` (`concert_search.artist`) and `cmd/job/sales-phase-discovery/main.go` (`ticket_sale_search.artist`), pass the item context to the use case, and end each span before the next artist; add a test annotated with "One trace per artist" that runs the loop for 3 artists with a fake use case and checks 3 linked item traces; verify it passes
- [x] 2.3 Start a run span in `cmd/job/sales-reminders`, `cmd/job/artist-image-sync` and `cmd/job/official-site-refresh` (`cmd/job/normalize-venue-names` is excluded, see design.md); add a test annotated with "Job that publishes events" that publishes one reminder event inside a run span and checks that the consumer span shares its trace id; verify it passes and `make check` is clean

## 3. Production check (read-only, after the backend release is rolled out)

- [x] 3.1 After the next `concert-discovery` run (daily 18:00 JST), read prod logs with `gcloud --configuration=liverty-music logging read` and confirm that `successfully received Gemini response` lines carry a `trace_id`, and that for one artist with new concerts the `auto-published new concerts for series` line from the `ingest-concert` consumer carries the same `trace_id`
- [x] 3.2 Open that trace in Cloud Trace and confirm one trace holds the artist span, the producer span and the consumer span, with a link to the run span
- [ ] 3.3 One week after the rollout, compare the Cloud Trace usage SKUs in the billing export with the week before and record the difference in this change's design.md
