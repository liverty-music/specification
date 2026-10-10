# components/infrastructure/fan/web/global/link-preview Specification

## Purpose
Link preview is the card that social networks and messengers (X, Facebook, LINE, Slack, Discord) show when a fan web link is shared: the Open Graph and X card tags carried in the HTML the fan web serves, built from the event for an Event page and site-wide otherwise.

## Requirements

### Requirement: Event page links carry the event's preview

The HTML served for `/events/:id` of an event with an event page SHALL carry, without running the app's scripts:
- `og:title`: the Series' title followed by " | " and the performing Artists' names, prefixed with "【公演中止】" when the Series is CANCELLED;
- `og:description`: the date with weekday, the doors-open and start times when announced and the venue name with its prefecture, all in Japanese with times in Japan time, followed by "全N公演" and the dates when the Series has more than one Event, then the start of the Series' description, at most 100 characters in total;
- `og:image`: the Series' cover image, or the brand default image when there is none, as an absolute URL;
- `og:url`: `https://liverty-music.app/events/<id>`, without any query parameter;
- `og:type` `website`, `og:site_name` `Liverty Music`, `og:locale` `ja_JP` with `og:locale:alternate` `en_US`;
- `twitter:card` `summary_large_image`.

#### Scenario: Shared on X

- **WHEN** an artist posts `https://liverty-music.app/events/<id>` on X for a Series titled "ONE MAN LIVE" by "The Band" on 2026-11-20 at Shibuya WWW, Tokyo
- **THEN** the card shows "ONE MAN LIVE | The Band", the date, times and venue in Japanese, and the cover image

#### Scenario: Link with a referral code

- **WHEN** the shared link is `/events/<id>?ref=member-a`
- **THEN** the preview's `og:url` is `https://liverty-music.app/events/<id>`

#### Scenario: Cancelled event

- **WHEN** the event's Series is CANCELLED
- **THEN** the preview title starts with "【公演中止】"

### Requirement: Site-wide preview otherwise

Every other fan web page, an `/events/:id` whose event has no event page, and an `/events/:id` whose event could not be read SHALL carry the site-wide preview: the product name, the site description and the brand default image. A failure to build an event's preview SHALL NOT prevent the page from loading for a fan.

#### Scenario: Unlisted event link

- **WHEN** a link to an UNLISTED event's `/events/:id` is shared
- **THEN** the card shows the site-wide preview, the same as for an unknown id

#### Scenario: Event read fails

- **WHEN** the event cannot be read while the HTML for `/events/<id>` is served
- **THEN** the HTML carries the site-wide preview and the Event page still loads for the fan

### Requirement: Edits reach new previews within a minute

A change to anything the preview is built from (the Series' title, description, cover image or publish state, the Event's date, times or venue) SHALL appear in the preview served for a newly requested `/events/:id` within 60 seconds. Previews that a social network has already cached are refreshed by that network's own tools.

#### Scenario: Series cancelled

- **WHEN** the organizer cancels the Series
- **THEN** the HTML served for its `/events/:id` 60 seconds later carries a title starting with "【公演中止】"
