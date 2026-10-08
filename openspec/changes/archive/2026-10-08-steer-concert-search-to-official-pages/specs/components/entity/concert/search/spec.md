## ADDED Requirements

### Requirement: Search reads the official site's concert pages

When the Artist has an official site, Search SHALL read the site's top page once before searching. Of the top page's links to pages of the official site's registrable domain, those whose path names a live, schedule, tour, concert or show page, and after them those whose path names a news page, SHALL be the pages Search reads first, at most 8 of them in total, each group in the order the page lists them. Links to other domains, and links whose path names none of those pages, SHALL be ignored. Search SHALL read at most the first 2 MB of the top page and take links from that part only. If the top page cannot be read — it fails to load within 5 seconds, answers with an error, redirects to a page of another registrable domain, or its host resolves to a private, loopback or link-local address — or it carries no such links, Search SHALL search as it does without them. If the site's host starts with `www.` and does not resolve, Search SHALL read the top page of the host without `www.` instead, and the registrable domain of that host SHALL be the official site's. A top page that cannot be read SHALL NOT fail Search.

#### Scenario: Concert pages linked from the top page
- **WHEN** the official top page `https://vaundy.jp/` links to `https://vaundy.jp/live/`, `https://member.vaundy.jp/feature/ASIAARENATOUR_2026` and `https://vaundy.jp/news/`
- **THEN** Search reads `https://vaundy.jp/live/` and `https://member.vaundy.jp/feature/ASIAARENATOUR_2026` first, then `https://vaundy.jp/news/`

#### Scenario: News pages after concert pages
- **WHEN** the official top page lists a news article before 8 same-domain live pages
- **THEN** Search reads the 8 live pages first and not the news article

#### Scenario: Link to another domain ignored
- **WHEN** the official top page links to a tour page on a ticket vendor's domain
- **THEN** Search does not list that page among the pages it reads first

#### Scenario: More than 8 concert links
- **WHEN** the official top page links to 12 same-domain live pages
- **THEN** Search reads the first 8 of them in page order

#### Scenario: Top page larger than 2 MB
- **WHEN** the official top page is 3 MB long and links to `https://vaundy.jp/live/` within its first 2 MB
- **THEN** Search reads `https://vaundy.jp/live/` first and does not fail

#### Scenario: Redirect to another domain
- **WHEN** the official top page redirects to a page on a link-sharing service's domain
- **THEN** Search searches as it does without links and does not fail

#### Scenario: Top page unavailable
- **WHEN** the official top page answers with HTTP 403
- **THEN** Search searches as it does without links and does not fail

#### Scenario: Private address refused
- **WHEN** the official site's host resolves to 10.0.0.5
- **THEN** Search does not request the page and searches as it does without links

#### Scenario: www host without DNS
- **WHEN** the official site is `http://www.super-beaver.com/`, `www.super-beaver.com` does not resolve and `super-beaver.com` serves the top page
- **THEN** Search reads the concert pages linked from `super-beaver.com`

## MODIFIED Requirements

### Requirement: Transient failures degrade to no results

Search SHALL retry a transient external failure — a timeout, rate limit, server error, temporary authorization failure or incomplete response — for up to 3 attempts in total. When every attempt fails transiently, Search SHALL return no concerts and no error. When the external service rejects the request as invalid, Search SHALL send it once more without the optional report of the external service's own tool calls, and SHALL fail with an error only if that request is rejected too. A permanent failure, a structurally broken response, a response that carries no candidate result, a response stopped because the model made too many tool calls, or the caller's own deadline or cancellation SHALL fail Search with an error; a response with no candidate result or stopped for too many tool calls SHALL NOT be retried within the same Search.

#### Scenario: Recovered on retry
- **WHEN** the first attempt times out and the second succeeds
- **THEN** Search returns the second attempt's concerts

#### Scenario: All attempts transient
- **WHEN** all 3 attempts are rate-limited
- **THEN** Search returns no concerts and no error

#### Scenario: Invalid request recovered without the tool report
- **WHEN** the external service rejects the request as invalid and accepts it without the tool-call report
- **THEN** Search returns the concerts of the second request

#### Scenario: Invalid request rejected twice
- **WHEN** the external service rejects the request as invalid with and without the tool-call report
- **THEN** Search fails with an error after those two requests

#### Scenario: Response without a candidate
- **WHEN** the external service answers successfully but with no candidate result
- **THEN** Search fails with an error after that one attempt

#### Scenario: Too many tool calls
- **WHEN** the external service stops the response because the model made too many tool calls
- **THEN** Search fails with an error after that one attempt

#### Scenario: Caller deadline expires
- **WHEN** the caller's deadline expires during Search
- **THEN** Search fails with an error
