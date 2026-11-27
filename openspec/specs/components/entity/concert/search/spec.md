# Concert.Search

## Purpose

Searches external sources for an Artist's announced concerts from the current date at their venue onward and returns them as DiscoveredSeries, grounded on the Artist's name and, when known, its official site.

## Requirements

### Requirement: Search returns grouped future events

Search SHALL return the Artist's concerts whose local date is on or after the current date at their Venue at the given time (see Venue) as DiscoveredSeries, one per tour or show, and two separately announced shows SHALL be two series even when they share a title. A series whose events are at two or more venues SHALL be a TOUR series; any other series, a one-off show or several days at one venue, SHALL be a SINGLE series. A venue not yet announced SHALL NOT count as a venue. Events dated before the current date at their Venue SHALL be left out, the Venue's time zone being the event's time zone (see "Time zone of each event"). An event whose time zone is unknown SHALL be left out only when its local date is before the current date in every time zone, that is, before the date at UTC−12 at the given time, so it is never left out while its date may still be today or later where it takes place. An Artist with no official site SHALL still be searched by name.

#### Scenario: Past event left out
- **WHEN** the source lists a show dated before the current date at its Venue
- **THEN** Search does not return it

#### Scenario: Yesterday's show early in the morning
- **WHEN** Search runs at 2026-11-10 23:30 UTC, which is 2026-11-11 at the Venue, and the source lists a show dated 2026-11-10
- **THEN** Search does not return it

#### Scenario: Time zone unknown, date possibly still today
- **WHEN** Search runs at 2026-11-11 08:00 UTC, which is 2026-11-10 at UTC−12, and the source lists a show dated 2026-11-10 whose time zone is unknown
- **THEN** Search returns it

#### Scenario: Time zone unknown, date past everywhere
- **WHEN** Search runs at 2026-11-11 13:00 UTC, which is 2026-11-11 at UTC−12, and the source lists a show dated 2026-11-10 whose time zone is unknown
- **THEN** Search does not return it

#### Scenario: Two standalone shows with one title
- **WHEN** the source lists two separately announced one-off shows with the same title
- **THEN** Search returns two SINGLE series

#### Scenario: Tour across venues
- **WHEN** the source lists a tour with dates at Zepp Nagoya and Taipei Arena
- **THEN** Search returns one TOUR series with both events

#### Scenario: Two days at one venue
- **WHEN** the source lists one show on 2026-11-25 and 2026-11-26 at LaLa arena TOKYO-BAY
- **THEN** Search returns one SINGLE series with both events

#### Scenario: No official site
- **WHEN** the Artist has no official site
- **THEN** Search still searches by the Artist's name

### Requirement: Search removes repeated events

Search SHALL return at most one event per local date, venue name and start time, keeping the first; two events at one venue on one date with different start times SHALL both be returned, and two with no start time SHALL collapse to one. Two venue names SHALL be the same when their normalized forms (see Venue, "Listed venue name normalization") are equal ignoring whitespace, middle-dot variants and Latin letter case; this covers full-width versus half-width characters, compatibility characters (such as the radical ⽇ for 日), middle-dot variants, whitespace and letter case. No other rule, such as a list of renamed venues or a prefecture in parentheses, SHALL make two venue names the same.

#### Scenario: First and second stage kept
- **WHEN** the source lists 2026-08-07 at one venue at 18:00 and at 21:00
- **THEN** Search returns both events

#### Scenario: Identical event listed twice
- **WHEN** the source lists the same date, venue and start time twice
- **THEN** Search returns it once

#### Scenario: Same venue in two notations
- **WHEN** the source lists one date and start time once at "渋谷CLUB QUATTRO" and once at "渋谷 CLUB QUATTRO"
- **THEN** Search returns it once

#### Scenario: Same venue in another letter case
- **WHEN** the source lists one date and start time once at "Zepp Haneda" and once at "ZEPP HANEDA"
- **THEN** Search returns it once

### Requirement: Search returns source text as written

Search SHALL return each event's venue name as the source wrote it, in its original language, without translating or romanizing it and without replacing it with another name for the same venue; annotations the source includes about the venue itself, such as a former name in parentheses, SHALL be kept, while show titles or subtitles printed next to the venue SHALL NOT be part of it. When the source is offered in several languages, its default-language version SHALL be the one copied. Each series' source page SHALL be the page dedicated to that tour when one exists, otherwise the official site's detail page for the concert. A date written without a year SHALL be returned with the year inferred from the page's context.

#### Scenario: Japanese venue on a multilingual page
- **WHEN** the source writes the venue as "幕張メッセ 9・11ホール" and also offers an English view
- **THEN** Search returns "幕張メッセ 9・11ホール"

#### Scenario: Default language of a multilingual tour page
- **WHEN** a tour page shows "北九州メッセ" by default and "Kitakyushu Messe" in its English version
- **THEN** Search returns "北九州メッセ"

#### Scenario: Show subtitle kept out of the venue
- **WHEN** the source lists "日本武道館" followed by the show subtitle "～PREMIUM LIVE on Xmas～"
- **THEN** Search returns the venue "日本武道館"

#### Scenario: Former name kept
- **WHEN** the source writes the venue as "クロコくんホール（旧 日本ガイシホール）"
- **THEN** Search returns "クロコくんホール（旧 日本ガイシホール）", not "日本ガイシホール"

#### Scenario: Year inferred from a two-year tour title
- **WHEN** a page titled "TOUR 2026-2027" lists "01.16. sat" after dates in 2026
- **THEN** Search returns 2027-01-16

### Requirement: Admin area is an ISO code or absent

Search SHALL return a venue's admin area only when the source states it or the venue makes it unambiguous, for a venue in any country, and only as the code of the first-level Area that the area resolves to without a country (see Area.Resolve): a code of any level or letter case, or an English or Japanese name. An area that does not resolve SHALL be returned as no admin area.

#### Scenario: Prefecture in Japanese
- **WHEN** the source gives the admin area "愛知県"
- **THEN** Search returns JP-23

#### Scenario: Prefecture in English
- **WHEN** the source gives the admin area "tokyo"
- **THEN** Search returns JP-13

#### Scenario: Overseas venue
- **WHEN** the show is at Taipei Arena in Taipei
- **THEN** Search returns TW-TPE

#### Scenario: State name
- **WHEN** the source gives the admin area "California" in free text
- **THEN** Search returns US-CA

#### Scenario: Lower-level code
- **WHEN** the area found for a venue in Bordeaux is FR-33
- **THEN** Search returns FR-NAQ

#### Scenario: Territory without subdivisions
- **WHEN** the show is at AsiaWorld-Arena in Hong Kong, given as HK or as CN-HK
- **THEN** Search returns HK

#### Scenario: Unrecognized area
- **WHEN** the source gives the admin area "Atlantis", or a well-formed code that is no Area such as JP-99
- **THEN** Search returns no admin area

#### Scenario: Name of areas in two countries
- **WHEN** the source gives the admin area "Victoria" and nothing else tells the country
- **THEN** Search returns no admin area

### Requirement: Unknown times are absent

Search SHALL return each event's start and open time as a time of day at the venue (hours and minutes), as the source states it, without converting it to another time zone, and only when the source gives a parseable time; a missing, "null" or unparseable time SHALL be returned as unknown. A time that does not exist on the event's date in the event's time zone, because a daylight saving change skips it, SHALL be returned as unknown. An event whose date cannot be parsed SHALL be left out.

#### Scenario: Literal null start
- **WHEN** the source's start time reads "null"
- **THEN** the event has no start time

#### Scenario: Show abroad keeps its local time
- **WHEN** the source lists a show in Seoul with "OPEN 17:30 / START 18:30"
- **THEN** Search returns the open time 17:30 and the start time 18:30

#### Scenario: Time skipped by daylight saving
- **WHEN** the source lists a show on 2027-03-14 starting at 02:30 at a venue whose time zone is America/New_York
- **THEN** the event has no start time

### Requirement: Transient failures are retried

Search SHALL retry a transient external failure — a timeout, rate limit, server error, temporary authorization failure or incomplete response — for up to 3 attempts in total. When every attempt fails transiently, Search SHALL fail with Unavailable, so the caller records a failed search rather than a search that found nothing. When the external service rejects the request as invalid, Search SHALL send it once more without the optional report of the external service's own tool calls, and SHALL fail with an error only if that request is rejected too. A permanent failure, a structurally broken response (including a response that ends normally with no text, since a result with no concerts is still a result), a response that carries no candidate result, a response stopped because the model made too many tool calls, or the caller's own deadline or cancellation SHALL fail Search with an error; a response with no candidate result or stopped for too many tool calls SHALL NOT be retried within the same Search.

#### Scenario: Recovered on retry
- **WHEN** the first attempt times out and the second succeeds
- **THEN** Search returns the second attempt's concerts

#### Scenario: All attempts transient
- **WHEN** all 3 attempts are rate-limited
- **THEN** Search fails with Unavailable after those 3 attempts

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

#### Scenario: Deadline passes during a call that then succeeds
- **WHEN** the caller's deadline passes while a call is in flight, and that call later returns concerts
- **THEN** Search fails with an error and returns no concerts

#### Scenario: Response without text
- **WHEN** the external service ends its response normally but with no text
- **THEN** Search fails with an error after that one attempt

### Requirement: Search covers the artist's own shows

Search SHALL return only the solo shows, co-headliner bills (対バン) and tours organized by the Artist. Music festivals and other multi-artist events at which the Artist is one of many performers SHALL be left out, and so SHALL shows announced as 中止 (cancelled), private events that are not open to the public, and shows held on a ship or at sea (a cruise), which have no fixed place and no ticket sold apart from the voyage.

#### Scenario: Festival left out
- **WHEN** the source lists the Artist among the lineup of a multi-artist music festival
- **THEN** Search does not return the festival

#### Scenario: Cancelled show left out
- **WHEN** the source lists a show of the Artist as 中止 (cancelled)
- **THEN** Search does not return it

#### Scenario: Co-headliner bill organized by the artist
- **WHEN** the source lists a two-act bill organized by the Artist
- **THEN** Search returns it as a SINGLE series

#### Scenario: Private event left out
- **WHEN** the source lists a show of the Artist with the venue "PRIVATE"
- **THEN** Search does not return it

#### Scenario: Show on a cruise ship left out
- **WHEN** the source lists a show of the Artist on the pool deck of a cruise ship during a voyage
- **THEN** Search does not return it

### Requirement: Each external call reports its usage

Every request Search sends to the external search model, including a retried or repeated one and one that fails, SHALL be reported once for product analytics as an LLM generation under the caller's trace, carrying: the model and its release, the release version of the backend, the Artist, its official site, the pages listed in the request and the start date; the input, output, thinking, tool-use and cached token counts as separate numbers; the latency; the web search queries the model issued, the sources it cited, and each page read with its result; the finish reason, any block reason, and the numbers of series and events parsed; and, for a failure, the kind of failure. The prompt text and the response body SHALL NOT be reported. A failure to report SHALL NOT change what Search returns.

#### Scenario: Search with a retry
- **WHEN** the first request fails transiently and the second succeeds
- **THEN** two generations are reported under the same trace, the first marked as a transient failure

#### Scenario: Grounded search
- **WHEN** the model issues 3 web search queries and reads 2 pages
- **THEN** the generation lists the 3 queries and the 2 pages with their results

### Requirement: Search lists the official top page's links

When the Artist has an official site, Search SHALL read the site's top page once before searching and SHALL list the top page's links in the request, each with its label — the link text, or else the alternative text of an image inside the link — in the order the page lists them, each link once, at most 60. The model, not Search, decides which listed pages announce shows. Links to any domain SHALL be listed except:

- links to domains that never carry an artist's official show announcements: social networks, music streaming, link hubs, shops, ticket vendors, fan-club and login platforms, and lyrics sites;
- links to pages of the official site's registrable domain whose path names a site-information, legal, artist-profile, discography or membership page (privacy, terms, contact, FAQ, profile, biography, discography, sign-in, account and the like).

A link to the official site's own registrable domain SHALL be listed even when that domain is one of the excluded third-party domains (an official site on `sites.google.com`). A link to the top page itself, a link whose URL is longer than 500 bytes, and the part of a label beyond its first 100 characters SHALL be left out. Labels SHALL be read in the character set the top page declares.

The official site passed in the request SHALL be the URL the top page was read from. Search SHALL read at most the first 2 MB of the top page and take links from that part only. If the top page cannot be read — it fails to load within 5 seconds, answers with an error, redirects to a page of another registrable domain, or its host resolves to a private, loopback or link-local address — or it carries no link to list, Search SHALL search as it does without them. If the site's host starts with `www.` and does not resolve, Search SHALL read the top page of the host without `www.` instead, and the registrable domain of that host SHALL be the official site's. A top page that cannot be read SHALL NOT fail Search.

#### Scenario: Links listed with their labels
- **WHEN** the official top page `https://vaundy.jp/` links to `https://vaundy.jp/live/` with the text "LIVE", to `https://member.vaundy.jp/feature/ASIAARENATOUR_2026` with an image whose alternative text is "ASIA ARENA TOUR 2026", and to `https://vaundy.jp/news/` with the text "NEWS"
- **THEN** the request lists `LIVE: https://vaundy.jp/live/`, `ASIA ARENA TOUR 2026: https://member.vaundy.jp/feature/ASIAARENATOUR_2026` and `NEWS: https://vaundy.jp/news/`, in that order

#### Scenario: Special show page without a concert word in its path
- **WHEN** the official top page links to `https://sp.super-beaver.com/feature/budokan2027` with an image whose alternative text is "武道館2027"
- **THEN** the request lists `武道館2027: https://sp.super-beaver.com/feature/budokan2027`

#### Scenario: Official tour site on another domain
- **WHEN** the official top page `http://gogovanillas.com/` links to `https://ggv-backhometour2027.jp`
- **THEN** the request lists that link

#### Scenario: Link to another domain ignored
- **WHEN** the official top page links to a tour page on a ticket vendor's domain and to the artist's account on a social network
- **THEN** Search does not list either link

#### Scenario: Site information page left out
- **WHEN** the official top page links to its own privacy policy, terms of use and discography pages
- **THEN** Search does not list those links

#### Scenario: More than 60 links
- **WHEN** the official top page carries 70 links that would be listed
- **THEN** Search lists the first 60 of them in page order

#### Scenario: Top page larger than 2 MB
- **WHEN** the official top page is 3 MB long and links to `https://vaundy.jp/live/` within its first 2 MB
- **THEN** the request lists `https://vaundy.jp/live/` and Search does not fail

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
- **THEN** Search lists the links of the top page of `super-beaver.com` and passes that page's URL as the official site

### Requirement: Time zone of each event

Search SHALL return each event's time zone as an IANA time zone name: the time zone of its admin area's Area when that Area has one; otherwise the time zone the source implies, when it is one of the time zones of the admin area's country; otherwise none. An event without an admin area SHALL have no time zone.

#### Scenario: Area with one time zone
- **WHEN** the event's admin area is JP-23
- **THEN** its time zone is Asia/Tokyo

#### Scenario: Area without a single time zone
- **WHEN** the event's admin area is US-TX, which has no time zone of its own, and the source implies America/Chicago
- **THEN** its time zone is America/Chicago

#### Scenario: Zone of another country
- **WHEN** the event's admin area is US-TX and the source implies Europe/London
- **THEN** the event has no time zone

#### Scenario: Area unknown
- **WHEN** the event has no admin area
- **THEN** the event has no time zone
