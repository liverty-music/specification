## MODIFIED Requirements

### Requirement: Search reads the official site's concert pages

When the Artist has an official site, Search SHALL read the site's top page once before searching. Of the top page's links to pages of the official site's registrable domain, those whose path names a live, schedule, tour, concert or show page, and after them those whose path names a news page, SHALL be the pages Search reads first, at most 8 of them in total, each group in the order the page lists them. Links to other domains, and links whose path names none of those pages, SHALL be ignored. Search SHALL read at most the first 2 MB of the top page and take links from that part only. If the top page cannot be read — it fails to load within 5 seconds, answers with an error, redirects to a page of another registrable domain, or its host resolves to a private, loopback or link-local address — or it carries no such links, Search SHALL search as it does without them. If the site's host starts with `www.` and does not resolve, Search SHALL read the top page of the host without `www.` instead, and the registrable domain of that host SHALL be the official site's. A top page that cannot be read SHALL NOT fail Search.

Search SHALL then read the first 3 of those pages whose path names a live, schedule, tour, concert or show page (not a news page), under the same limits as the top page. The links of those concert pages that point to the official site's registrable domain, other than the top page and the pages the top page links to, SHALL also be pages Search reads first, after the pages taken from the top page, in the order the concert pages list them, whatever their path. Search SHALL list at most 20 pages in total. A concert page that cannot be read SHALL be skipped and SHALL NOT fail Search.

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

#### Scenario: Tour detail pages behind a live page
- **WHEN** the official top page `https://example.jp/` links to `https://example.jp/live/` and `https://example.jp/goods/`, and `https://example.jp/live/` links to `https://example.jp/live/tour-a/`, `https://example.jp/contents/123` and `https://example.jp/goods/`
- **THEN** Search reads `https://example.jp/live/` first, then `https://example.jp/live/tour-a/` and `https://example.jp/contents/123`, and does not list `https://example.jp/goods/`

#### Scenario: Only the first 3 concert pages followed
- **WHEN** the official top page links to 5 same-domain live pages
- **THEN** Search reads the links of the first 3 of them and not of the other 2

#### Scenario: News page not followed
- **WHEN** the official top page links to `https://example.jp/news/`, and that page links to 10 news articles
- **THEN** Search does not list those articles

#### Scenario: Concert page link to another domain ignored
- **WHEN** a concert page links to a tour page on a ticket vendor's domain
- **THEN** Search does not list that page among the pages it reads first

#### Scenario: At most 20 pages
- **WHEN** the official top page gives 4 pages and its concert pages link to 30 other same-domain pages
- **THEN** Search lists the 4 pages and the first 16 of the 30

#### Scenario: Concert page unavailable
- **WHEN** the official top page links to `https://example.jp/live/` and that page answers with HTTP 403
- **THEN** Search reads the pages taken from the top page and does not fail
