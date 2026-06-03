# merch-discovery Specification

## Purpose

The Merch Discovery capability keeps `Series.merch_url` populated and healthy via a dedicated, time-windowed scheduled job. It resolves the single official page that carries a tour's merchandise information (official site or official social media) close to when that information is actually published, and revalidates existing links so dead ones are cleared and re-resolved. It deliberately stores only the link — no sale timing, channel, price, or item data — and runs independently of concert discovery.

## Requirements

### Requirement: Scheduled Merch URL Discovery Job

The system SHALL provide a scheduled job that resolves and maintains `Series.merch_url`. The job SHALL run on a recurring schedule — daily in production and weekly in development — mirroring the concert-discovery job's cadence. The job SHALL NOT extend or depend on the concert-discovery Gemini crawl.

#### Scenario: Scheduled execution

- **WHEN** the merch-url discovery job is triggered on its schedule
- **THEN** it SHALL load the set of candidate series, resolve each candidate's merch URL, and persist any resolved URLs
- **AND** it SHALL run independently of the concert-discovery job

### Requirement: Candidate Selection by Earliest Event and Missing Link

The job SHALL consider a series a candidate when its **earliest** event's `local_date` falls within the window `[today, today + 60 days]` and its `merch_url` is empty or has been determined to be a dead link. Series whose earliest event is more than 60 days away, or already in the past, SHALL NOT be candidates.

#### Scenario: Series with an upcoming earliest event and no merch URL

- **WHEN** a series has `merch_url` empty and its earliest event's `local_date` is within the next 60 days
- **THEN** the series SHALL be selected as a candidate

#### Scenario: Earliest event beyond the window

- **WHEN** a series has `merch_url` empty and its earliest event's `local_date` is more than 60 days away
- **THEN** the series SHALL NOT be selected
- **AND** it SHALL become a candidate on a later run once its earliest event enters the 60-day window

#### Scenario: Series already populated with a live URL

- **WHEN** a series has a non-empty `merch_url` that passes the liveness check
- **THEN** the series SHALL NOT be re-searched
- **AND** its existing `merch_url` SHALL be left unchanged

### Requirement: Dead-Link Revalidation

For an in-window series whose `merch_url` is non-empty, the job SHALL perform an HTTP liveness check before deciding whether to re-search. A response that is a definitive non-2xx and non-3xx status (or a hard request failure) SHALL be treated as a dead link: the job SHALL clear `merch_url` to empty and treat the series as a candidate for re-search. A transient or ambiguous result (timeout, network error, or a bot-blocking response that is not a definitive failure) SHALL be treated as alive, leaving `merch_url` unchanged.

#### Scenario: Dead link is cleared and re-searched

- **WHEN** an in-window series' `merch_url` returns a definitive non-2xx/3xx status
- **THEN** the job SHALL clear `merch_url`
- **AND** the series SHALL be re-searched in the same run

#### Scenario: Transient failure does not clear the link

- **WHEN** an in-window series' `merch_url` liveness check times out or returns an ambiguous result
- **THEN** the job SHALL leave `merch_url` unchanged
- **AND** the series SHALL NOT be re-searched on that basis

### Requirement: Gemini Merch URL Resolution Restricted to Official Sources

For each candidate, the job SHALL call Gemini Flash-Lite with search grounding, supplying the performing artist name and the series title, and SHALL request the single URL that carries the richest merch sales information. The result SHALL be sourced only from the artist's official website or official social media accounts. When no confident official source exists, the job SHALL return an empty result rather than a non-official or low-confidence URL. The resolved value MAY be a social-media post URL.

#### Scenario: Confident official merch URL found

- **WHEN** Gemini identifies a single best merch URL on the official site or official social media
- **THEN** the job SHALL treat that URL as the resolution result

#### Scenario: No confident official source

- **WHEN** Gemini finds no merch information from an official site or official social media account
- **THEN** the job SHALL return an empty result
- **AND** the job SHALL NOT persist any URL for that series on this run

#### Scenario: Richest source is a social-media post

- **WHEN** the official social media post carries fuller merch information than the official site
- **THEN** the job MAY resolve `merch_url` to that social-media post URL

### Requirement: Fill-Once Persistence of Resolved URL

The job SHALL persist a resolved URL only when the series' `merch_url` is empty (including a value just cleared as a dead link). It SHALL NOT overwrite a `merch_url` that passed the liveness check. Every persisted value SHALL satisfy the `Url` value-object constraints; a value failing validation SHALL be discarded and the field left empty.

#### Scenario: Resolved URL persisted for an empty field

- **WHEN** the job resolves a valid official URL for a series whose `merch_url` is empty
- **THEN** the job SHALL persist that URL to `Series.merch_url`

#### Scenario: Invalid URL discarded

- **WHEN** a resolved value fails `Url` validation
- **THEN** the job SHALL NOT persist it
- **AND** `merch_url` SHALL remain empty

### Requirement: Job Resilience

The job SHALL isolate per-series failures and SHALL always exit successfully so that the schedule is not disrupted. A per-series resolution or persistence failure SHALL NOT abort the run. The job SHALL stop early via a circuit breaker after a configured number of consecutive failures, and a successful resolution SHALL reset the consecutive-failure counter.

#### Scenario: Individual series failure is non-fatal

- **WHEN** resolving or persisting one series fails
- **THEN** the job SHALL continue processing the remaining candidates
- **AND** the job SHALL still exit successfully

#### Scenario: Circuit breaker on consecutive failures

- **WHEN** the configured number of consecutive failures is reached
- **THEN** the job SHALL stop processing further candidates
- **AND** the job SHALL exit without surfacing a non-zero failure that would disrupt the schedule

#### Scenario: Successful resolution resets the counter

- **WHEN** a series is resolved successfully after prior failures
- **THEN** the consecutive-failure counter SHALL reset to zero
