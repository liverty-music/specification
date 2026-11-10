## Context

See proposal.md for why. Today the schema's specs instruction ("Layer contents") requires an erDiagram and a stateDiagram-v2 in an entity's Purpose, and a usecase-beta diagram in a story's Purpose. `scripts/check-story-diagrams.py` enforces the story diagram in pre-commit (`.pre-commit-config.yaml`), `make check` and the `openspec-checks` CI job. It checks that every usecase method a story names appears in the fence. The schema also says "Order is not drawn: it is the scenarios'", so no diagram shows the order in which a story's usecases run.

Usecase, adapter and infrastructure specs have no diagrams. In the backend, the usecases of a story are connected by events: an entity operation announces an event (outbox), and a consumer behavior in `internal/di/consumer.go` runs the next usecase, or starts a workflow that runs it. The specs describe each announcement in prose ("the Order is announced as paid once"), but they never name the event.

Mermaid facts this design relies on:
- `eventmodeling` was added in Mermaid 11.15 (heading "Event Modeling Diagram (v11.15.0+)" at https://mermaid.ai/open-source/syntax/eventmodeling.html). `usecase-beta` was added in 12.0 (the use case diagram page of the same docs). The latest release is 12.3.0, published 2026-11-03 (`gh release list -R mermaid-js/mermaid`).
- The project targets the latest Mermaid. Older bundled renderers are not supported. VS Code 1.145.2 bundles Mermaid 11.17.2 in its built-in `mermaid-markdown-features` extension (`version:"11.17.2"` in `extensions/mermaid-markdown-features/markdown-preview-out/index.js` of the install). That bundle contains the `eventmodeling` diagram but not `usecase-beta`.
- The naming and link conventions in decision 1 come from a render spike on 2026-11-10: Mermaid 12.3.0 and 11.17.2 from jsdelivr, rendered in headless Chromium with Playwright.

## Goals / Non-Goals

**Goals:**
- A reader sees in one diagram how a story moves from the first screen to the last: who acts, which usecase runs, which event connects it to the next usecase.
- A reader sees in one diagram the call order and the branches of a long usecase.
- Domain events become named vocabulary, so stories, diagrams and later changes can refer to them.
- Every diagram is checked against the prose it summarizes, so the two cannot drift apart.

**Non-Goals:**
- Diagrams for screen, surface, adapter and webhook specs.
- Renaming backend event subjects to match the event names defined here. This is a separate change; the mapping below records the current difference.
- A CI step that renders Mermaid. The checks compare names only, as `check-story-diagrams.py` does today.

## Decisions

### 1. Stories are drawn as an Event Modeling diagram

The story's Purpose holds one `eventmodeling` fence, replacing the usecase-beta fence. The elements map to the spec tree as follows:

| element | stands for | name |
|---|---|---|
| `ui` | a screen or surface an actor uses | `<Actor>_<Screen>`, where Actor is one of fan, member, admin or venue staff in PascalCase (`Fan`, `Member`, `Admin`, `VenueStaff`), and Screen is the route or global surface spec name in PascalCase (`Fan_Tickets`, `Fan_EventDetailSheet`) |
| `cmd` | a usecase method that writes | `<Interface>_<Method>` (`LotteryEntryUseCase_Confirm`) |
| `rmo` | a usecase method that only reads, whose result a screen shows | `<Interface>_<Method>` (`TicketUseCase_List`) |
| `evt` | a domain event an entity lists (decision 2) | `<Entity>_<PastTense>` (`LotteryEntry_Drawn`) |
| `pcr` | a trigger with no actor: a schedule, or a call from an external system | `Schedule_<What>` or `External_<System>` (`Schedule_DrawWindowClosed`, `External_PaymentProvider`) |

Rules:
- **A usecase run by an event** directly follows that event (`evt` → `cmd`). The consumer and any workflow between them are implementation and are not drawn.
- **A usecase run by a schedule** follows its `pcr`.
- **One event starting several usecases** is drawn with explicit links: `rf NN cmd ... ->> MM`, where `MM` is the event's frame.
- **Branch conditions** (won or lost, captured or not) are not drawn. They stay in the scenarios.
- **What the fence contains**: every usecase method the story names, as a `cmd` or `rmo`. It may also contain a method the story describes only in words.

Why the `_` separator: in `eventmodeling`, a dotted name (`LotteryEntryUseCase.Confirm`) is read as a namespace, and every namespaced frame gets its own lane, even when it repeats a namespace. In the render spike (Mermaid 12.3.0 and 11.17.2), the lottery story grew to 15 lanes this way. Quoted and backticked names fail to parse. With `_`, the diagram keeps the three standard lanes and the full names. The check maps the first `_` back to `.`.

Alternatives considered:
- **sequenceDiagram**: it can draw branches, but it has no notion of an event or a screen. Event-driven hand-offs would have to be faked with an "Events" participant.
- **swimlane-beta**: it is a flowchart with lanes. It also has no event element, and it adds a second flow notation.
- **Keeping usecase-beta next to the new diagram**: two diagrams per story to maintain. The usecase-beta diagram would add only the actor edges, and the `ui` lanes already show those.

### 2. Domain events are listed in the entity's Purpose

An event is about one entity: the one the operation announces ("announce that Event as cancelled" is about the Event). That entity lists the event in its Purpose, after the attribute table, as a table with the columns event | announced by | carries:
- **event**: the name, `<Entity>.<PastTense>`, where Entity is the entity the event is about. The prose "announce X as Y" becomes `X.Y`.
- **announced by**: the operations that announce it. They may belong to another entity: Series.CancelEvents announces Event.Cancelled, and Order.Issue announces ResaleListing.Sold.
- **carries**: what the event holds, in attribute terms.

The name says what happened to the entity, in its own vocabulary (`Order.Paid`, not `Order.Issued`, because the operation is Issue but what the event tells is that the Order is Paid). An event that today means "something changed" is named for what the operation records. Splitting such an event into precise ones is part of the separate subject change.

Diagrams use the same names with `_`.

The operations' own requirements already state when they announce ("announced with the change") and stay as they are. The table only gives each announcement a name.

Current backend subjects and the event names they are expected to get. The apply step confirms each name by reading what the announcing operation's spec says it announces:

| backend subject | event |
|---|---|
| `CONCERT.created` | Concert.Created |
| `CONCERT.cancelled` | Event.Cancelled (announced by Series.CancelEvents) |
| `ARTIST.created` | Artist.Created |
| `ARTIST.followed` / `ARTIST.unfollowed` | Follow.Created / Follow.Deleted |
| `ARTIST.hype_changed` | Follow.HypeChanged |
| `USER.created` | User.Created |
| `USER.logged_in` | User.LoggedIn |
| `USER.passkey_added` / `USER.passkey_removed` | Passkey.Added / Passkey.Removed |
| `NOTIFICATION.subscribed` / `NOTIFICATION.unsubscribed` | PushSubscription.Created / PushSubscription.Deleted |
| `SALES_PHASE.discovered` | TicketSale.Discovered |
| `TICKET_JOURNEY.status_changed` | TicketJourney.StatusChanged |
| `ORGANIZER.created` | Organizer.Activated |
| `ORGANIZER.artist_associated` | Organizer.ArtistAssociated |
| `SERIES_IMAGE.uploaded` | SeriesImage.Uploaded |
| `ORDER.paid` | Order.Paid |
| `ORDER.refunded` | Order.Refunded |
| `ORDER.resale_listing_sold` | ResaleListing.Sold (announced by Order.Issue) |
| `ORDER.resale_listing_refunded` | ResaleListing.Refunded |
| `ORDER.lottery_entry_entered` | LotteryEntry.Entered |
| `ORDER.lottery_entry_drawn` | LotteryEntry.Drawn |
| `ORDER.resale_entry_changed` | ResaleEntry.Changed |
| `ORDER.checkout_held` / `ORDER.checkout_expired` / `ORDER.checkout_released` | Checkout.Held / Checkout.Expired / Checkout.Released |
| `ORDER.ticket_admitted` | Ticket.Admitted |

### 3. Long usecases are drawn as a sequence diagram

A usecase spec whose text outside the fence names 5 or more distinct entity operations holds one `sequenceDiagram` fence in its Purpose. An entity operation is a name `<Entity>.<Operation>` whose Entity has a spec under `components/entity/`.

Conventions:
- **Participants**: the first participant is `participant UC as <Interface>.<Method>`. Then comes one `participant <Entity>` per entity it calls, named exactly as the entity.
- **Messages**: each call is `UC->><Entity>: <Operation>`, optionally followed by a short argument note (`UC->>LotteryEntry: RevertWin "concert cancelled"`). A call to another method of the same usecase interface is `UC->>UC: <Method>`.
- **Branches**: `alt`/`else`, `opt`, `loop` and `break` carry the branches the requirements state, labelled in the requirements' own terms (`alt Order is Paid`). Retries and time limits are a `Note over`. `autonumber` is on.
- **Triggers**: an entity operation the text names as what starts the usecase, rather than as a call it makes, is drawn as an incoming dashed message before the first call: `LotteryEntry-->>UC: PersistDrawOutcome (Won)`. For example, OrderUseCase.Issue runs once for each entry LotteryEntry.PersistDrawOutcome records Won. A usecase method of another interface that starts it (OrderUseCase.Place) is written in a `Note over UC` and is not a message, since it is not an entity operation.
- **Coverage**: the set of `<Entity>.<Operation>` pairs in the messages, calls and triggers together, equals the set named in the text. The diagram adds no operation that the requirements do not name, and leaves none out. Drawing a trigger as a call is wrong, even though the check cannot tell the two apart.

The diagram summarizes the requirements and is not normative. When the two disagree, the requirements win and the diagram is fixed.

The threshold is computed, not judged, so the check can enforce it. Today it selects 37 specs.

Alternative considered: a flowchart for decision-heavy usecases (TicketUseCase.Admit). It was rejected because one notation per layer keeps the rule simple, and `alt`/`break` cover Admit's reject reasons.

### 4. One check script for all three diagrams

`scripts/check-story-diagrams.py` becomes `scripts/check-diagrams.py`. Main specs only, as today; names are matched as text, and the Mermaid is not parsed. It checks three things:
- **Stories**: every `UseCase.Method` the story names outside its Purpose's fence appears in the `eventmodeling` fence as a `cmd` or `rmo` (with `_` mapped back to `.`). A story that names a usecase method has the fence.
- **Events**: every `evt` in a story fence is listed in some entity's events table, and no event name is listed twice.
- **Usecases**: a usecase spec that names 5 or more distinct entity operations has a `sequenceDiagram` fence in its Purpose. The fence's messages name exactly the entity operations its text names.

Entity names are matched to spec directories case-insensitively with hyphens removed, so acronyms resolve (`Event.GetOrganizerID` → `event/get-organizer-id`).

The pre-commit hook id, the `make check` target and the CI step are renamed with it.

Why one script: the three checks share the Purpose and fence parsing, and one hook is one more concept fewer than three.

### 5. Purpose edits land in one specification PR

All Purposes are edited directly in the main specs, as the schema already requires for entity and story Purposes. The schema text, the check script and the spec edits go in one PR from a specification worktree, so the check passes on the first commit that adds it. The schema change extends the "edited directly in the main spec" rule to a usecase's Purpose diagram. A later change that modifies a usecase's requirements lists that usecase marked (Purpose) and fixes its diagram when it archives; the check on main specs fails until it does.

### 6. Every new fence is rendered once before the PR

The check does not parse Mermaid, so a syntax error would show only as a broken diagram on GitHub. During the apply step, every new or changed fence is rendered with Mermaid 12.3.0 in headless Chromium (the spike's approach: Playwright from frontend's `node_modules`, scripts kept outside the repository). The run must end with no parse error. This is a one-time check for this change, not a CI step.

## Risks / Trade-offs

- [Mermaid parse errors are not caught by CI] → The one-time render in decision 6 covers this change. Later edits are reviewed on the PR preview. A CI render step can be added if broken diagrams appear.
- [Wide story diagrams: a story with 15 usecases draws about 20 frames, roughly 2500px wide] → Accepted. GitHub scrolls the diagram horizontally, and the time order is the point of the diagram.
- [`eventmodeling` and its `->>` links are new; layout or syntax may change in later Mermaid releases] → The diagram keeps to the documented frame syntax. A breaking release would show on every story at once, and so would be noticed quickly.
- [Event names differ from backend subject strings until the separate change aligns them] → The mapping table in decision 2 records each difference.
- [The 5-operation threshold counts every name in the prose, triggers included, so a usecase that makes few calls but names many triggers (OrderUseCase.ReleaseCardAuthorization) needs a diagram. Rewording can also move a spec across the threshold] → Accepted. A usecase started from many places is hard to follow too, and the trigger messages show where it starts. The check then requires the diagram, or it is no longer required, and either way the spec stays consistent.
