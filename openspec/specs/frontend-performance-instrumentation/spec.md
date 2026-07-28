# frontend-performance-instrumentation Specification

## Purpose
TBD - created by archiving change discovery-perf-instrumentation-and-bubble-cap. Update Purpose after archive.
## Requirements
### Requirement: Long animation frames reported to analytics
The frontend SHALL observe long animation frames (frames taking longer than 100ms) across all pages using the Long Animation Frames API and report them to the product analytics service (PostHog).

#### Scenario: Long frame detected
- **WHEN** a browser animation frame takes longer than 100ms
- **THEN** the system SHALL capture a `perf.long_animation_frame` event to PostHog containing the frame duration in milliseconds, the source function name, the source script URL, and the current route pathname
- **AND** the observer SHALL be registered once at application bootstrap and active for the entire session

### Requirement: Core Web Vitals reported to analytics
The frontend SHALL measure and report LCP, INP, and CLS to PostHog using the `web-vitals` library, enabling ongoing monitoring of real-user performance across all pages and SPA route navigations.

#### Scenario: Core Web Vital measured
- **WHEN** a Core Web Vital (LCP, INP, or CLS) value is determined for a page view or soft navigation
- **THEN** the system SHALL capture a `web.vitals` event to PostHog containing the metric name, value in milliseconds (or unitless for CLS), rating (`good` / `needs-improvement` / `poor`), navigation type, and current route pathname
- **AND** only the final stable value SHALL be reported (not intermediate updates)

### Requirement: Slow interactions reported to analytics
The frontend SHALL observe individual user interaction latencies using the Event Timing API and report interactions slower than 150ms to PostHog.

#### Scenario: Slow interaction detected
- **WHEN** a user interaction (pointer down, key press, click) has a processing duration greater than 150ms
- **THEN** the system SHALL capture a `perf.slow_interaction` event containing the interaction type, duration in milliseconds, and current route pathname
- **AND** the PerformanceObserver SHALL be registered without a `durationThreshold` option (accepting the browser minimum of 104ms), and the 150ms threshold SHALL be applied as a JavaScript filter in the callback — NOT as `durationThreshold: 150`, which would miss 104–149ms events

