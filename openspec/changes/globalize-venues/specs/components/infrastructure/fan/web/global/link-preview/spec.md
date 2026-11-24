## MODIFIED Requirements

### Requirement: Concert page links carry the event's preview

The HTML served for `/concerts/:id` of an event with a concert page SHALL carry, without running the app's scripts:
- `og:title`: the Series' title followed by " | " and the performing Artists' names, prefixed with "【公演中止】" when the event is CANCELLED;
- `og:description`: the date with weekday, the doors-open and start times when announced and the venue name with its prefecture, all in Japanese, with the date and times at the Venue's local time followed by the Japanese name of the Venue's time zone and 時間 (`日本時間`, `ロンドン時間`), followed by "全N公演" and the dates when the Series has more than one Event, then the start of the Series' description, at most 100 characters in total;
- `og:image`: the Series' cover image, or the brand default image when there is none, as an absolute URL;
- `og:url`: `https://liverty-music.app/concerts/<id>`, without any query parameter;
- `og:type` `website`, `og:site_name` `Liverty Music`, `og:locale` `ja_JP` with `og:locale:alternate` `en_US`;
- `twitter:card` `summary_large_image`.

#### Scenario: Shared on X

- **WHEN** an artist posts `https://liverty-music.app/concerts/<id>` on X for a Series titled "ONE MAN LIVE" by "The Band" on 2026-11-20 at Shibuya WWW, Tokyo
- **THEN** the card shows "ONE MAN LIVE | The Band", the date, times with 日本時間 and venue in Japanese, and the cover image

#### Scenario: Event abroad

- **WHEN** the link is to an event on 2027-02-20 with OPEN 18:30 and START 19:30 at a Venue in London
- **THEN** the description shows 2月20日(土) with OPEN 18:30 and START 19:30 followed by ロンドン時間, and no Japan time

#### Scenario: Link with a referral code

- **WHEN** the shared link is `/concerts/<id>?ref=member-a`
- **THEN** the preview's `og:url` is `https://liverty-music.app/concerts/<id>`

#### Scenario: Cancelled event

- **WHEN** the event is CANCELLED
- **THEN** the preview title starts with "【公演中止】"
