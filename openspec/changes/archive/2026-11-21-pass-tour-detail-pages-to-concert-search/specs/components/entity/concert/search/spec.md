## ADDED Requirements

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

## REMOVED Requirements

### Requirement: Search reads the official site's concert pages
**Reason**: Replaced by "Search lists the official top page's links". Choosing the concert pages by keywords in their paths missed show pages without such a word (`feature/budokan2027`) and official tour sites on other domains; the model now chooses among the labeled links (OpenSpec change pass-tour-detail-pages-to-concert-search, design D7).
**Migration**: None. The fetch limits, the failure handling and the `www.` fallback carry over to the new requirement.
