## Why

Concert discovery does not recognize that two found events are one concert, or that two found tours are one tour (liverty-music/backend#926). In production on 2026-11-27, 9 upcoming concerts were listed twice under two venue names, one tour was split over up to 3 TOUR Series for 13 Artists (29 Series), no discovered concert had more than one performer, and on 2026-11-20 one `create-from-discovered` run failed as a whole when it filled a start time that another Event already held.

## What Changes

- An Artist's existing Event at the same Venue and date counts as the same concert whatever its listed venue name, so a start time is filled onto it instead of publishing a second Event. A different listed name for the same slot is staged for the admin as today.
- An Event of the same Artist on the same date with the same known start time at another Venue (a renamed hall, a building and its hall) is a collision and is staged.
- An Event keeps the listed venue names an admin did not choose when resolving a duplicate, and a later discovery under such a name is a re-discovery, so the same candidate is not staged again.
- Another Artist's discovered Event at the same slot is one concert with two performers: discovery adds the Artist as a performer when the listed venue name and the known start time match, and stages it otherwise; approving such a candidate with either resolution adds the performer. An Organizer's Event is never changed this way; it is staged as today.
- When the start time to fill is held by another Artist's Event, the Artist's start-time-less Event is merged into it (performers and fans' ticket journeys move, nobody is notified again): automatically when the listed names match, on approval otherwise. A collision no longer fails the batch.
- A discovered TOUR joins the Artist's TOUR Series of the same title that has an upcoming Event, so dates announced later stay in their tour; a series also joins through an Event at the same Venue, not only the same listed name. Venues are resolved before the series is chosen.
- The approval queue's conflict dialog says that either choice keeps one Event and lists the candidate's Artist as its performer.
- A one-off data migration merges the 9 duplicate pairs and folds the 29 split TOUR Series into 13.
- A listing an admin rejected, or settled with keep existing, is not staged again while it is found unchanged: discovery leaves out a found event that is the same listing (same Artist, date, listed venue and start time) as a RejectedConcert entry. Until now a duplicate whose venue could not be resolved came back after every rejection, since approving it would create a Venue from its listed name. A corrected listing (another start time, venue or date) is still reviewed again. A venue name that only says the venue is announced later, such as "会場後日発表予定", is a missing name.
- Discovery processes one batch at a time, so two Artists of one concert found at the same time no longer race. Empty discovered Series are removed by a daily run instead of right after they are emptied.

## Capabilities

### New Capabilities
- `components/entity/concert/merge`: merges a discovered Event into another discovered Event at the same Venue and date, moving its performers and its fans' ticket journeys and sale links, without announcing anything.
- `components/entity/concert/add-other-listed-venue-name`: records a listed venue name an Event is also known by.
- `components/usecase/series/remove-empty-discovered-series`: removes empty discovered Series once a day.
- `components/entity/rejected-concert/list-by-artist`: lists an Artist's RejectedConcert entries.
- `components/entity/series/list-upcoming-tours-by-artist`: lists an Artist's discovered TOUR Series that still have an Event on or after the current date at its Venue, with their titles.

### Modified Capabilities
- `components/usecase/concert/create-from-discovered` (and Purpose diagram at archive): series joining by Venue and by tour title, matching the Artist's Events by Venue and by other listed names, the same Artist at another Venue at the same time, another Artist's slot, a start time held by another Event, no failed batch on a collision, one batch at a time, and no Series removal at the end of a batch.
- `components/usecase/concert-candidate/approve` (and Purpose diagram at archive): collision with the Artist's Event at another Venue, a non-colliding candidate fills only its own Artist's Event, both resolutions add the Artist as performer of another Artist's Event (merging the Artist's start-time-less Event), and the name not chosen is recorded on the Event; the emptied Series is no longer removed.
- `components/entity/concert/fill-event-start-times`: fails with AlreadyExists, changing nothing, when another Event holds the slot.
- `components/entity/concert/update-event-listed-venue-name`: keeps the replaced name among the Event's other listed venue names.
- `components/entity/concert/find-events-by-artist-and-date`, `components/entity/concert/find-events-by-venue-and-date`: also return the Event's other listed venue names, publish state and performers.
- `components/entity/series`: when a discovered tour title is the same as a Series title.
- `components/infrastructure/admin/web/route/approval-queue`: the conflict dialog's wording.
- `stories/review-concert-candidates`: approving a shared bill.
- `components/entity/event` (Purpose and a new requirement): new attribute "other listed venue names"; an Event is listed under a name when its listed venue name or one of its other listed venue names is that name.
- `components/entity/concert/create`: fails when an Event with a publish state holds a slot, so an Organizer who publishes while a discovery or an approval is storing a Concert keeps the Event as published.
- `components/entity/series/delete-orphaned` (and Purpose at archive): removes empty discovered Series by age, keeping one with a TicketSale or being written.
- `components/usecase/concert-candidate/reject` (and Purpose at archive: its diagram, and that the rejection keeps the same listing out of discovery): no longer removes the emptied Series.
- `components/entity/rejected-concert` (and Purpose at archive: the log also keeps discovery from staging the same listing): "The log never suppresses" becomes "Same listing", the rule discovery uses to leave out a settled listing.
- `components/usecase/concert/search-new-concerts` (and Purpose diagram at archive: a `RejectedConcert.ListByArtist` call and the drop after the pending one): leaves out the same listing as one of the Artist's RejectedConcert entries.
- `components/entity/venue`: "会場未定", "会場後日発表予定" and similar names are missing names.
- `stories/review-concert-candidates` (and Purpose at archive: a rejected concert is reviewed again only with a corrected listing): "Rejection is not permanent" becomes "Only a corrected listing is reviewed again".
- Relied on and unchanged: ConcertCandidate.Upsert, Series.Create, Venue lookups, RejectedConcert.Append (keep existing still records the candidate, which now also keeps that listing out of discovery).

## Impact

- backend: `internal/usecase/concert_creation_uc.go` and `concert_candidate_uc.go` (shared collision rules), the concert and series repositories, a new column or table for other listed venue names, and an Atlas data migration for the listed duplicates and split Series. A backend merge applies the migrations to prod.
- frontend: the admin approval-queue conflict dialog wording.
- specification: comment-only update of `ApproveResolution` in the admin concert candidate proto (no type change), and of the `ConcertCandidateService` comment that says a rejection is not permanent.
- No fan-facing API change. Out of scope: merging Venue rows, a failed creation still starting the discovery window (liverty-music/backend#929), clearing the 153 pending candidates that differ only by listed name, SINGLE Series and tours whose title changes between searches.
