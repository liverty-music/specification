## Why

The specs say what happens in prose, and the prose is hard to follow where the logic is longest. None of the 143 usecase specs has a diagram, although 37 of them call 5 or more distinct entity operations (components/usecase/order/issue calls 21, over 186 lines and 32 scenarios). A story's usecase-beta diagram lists the usecases it composes but not the order they run in or what connects them. In the backend, the usecases a story composes are connected by events: one usecase announces an event, and a consumer runs the next usecase (about 37 consumer behaviors). The specs describe these announcements in prose but never name them, so a reader cannot see how one story step leads to the next.

## What Changes

- **Story diagrams**: a story's Purpose draws the story as a Mermaid `eventmodeling` diagram, replacing the usecase-beta fence. The diagram shows, in time order, the screens the actors use, the write usecases they call, the domain events those usecases announce, the usecases those events start, the schedules that start usecases, and the read usecases whose results the screens show. Branch conditions (won or lost, success or failure) stay in the scenarios.
- **Domain events as vocabulary**: an entity's Purpose lists, as a table, the domain events announced about it and the operations that announce them. Each event is named `<Entity>.<PastTense>` (LotteryEntry.Drawn). Story diagrams use only listed events.
- **Usecase diagrams**: a usecase spec whose requirements name 5 or more distinct entity operations draws its flow in its Purpose as a Mermaid `sequenceDiagram`. The participants are the usecase and the entities it calls, each message is one entity operation, and `alt`, `opt`, `loop` and `break` show the branches.
- **Checks**: one script, scripts/check-diagrams.py, replaces scripts/check-story-diagrams.py. It checks a story's eventmodeling fence instead of the usecase-beta fence, that every event a story draws is listed by an entity, and the usecase diagram rule.
- **Schema**: the liverty-clean-arch schema's specs instruction ("Layer contents" and "What may be named") states the three rules above, so later changes follow them.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None through a delta. This change edits only the Purpose of existing main specs, which the schema says is edited directly in the main spec, so the change sets `skip_specs: true`. No requirement or scenario changes. The Purposes edited are:
- every story under `stories/` that names a usecase method (Purpose): the eventmodeling diagram replaces the usecase-beta diagram;
- every entity under `components/entity/` that some operation announces an event about (Purpose): the events table;
- the 37 usecase specs under `components/usecase/` whose requirements name 5 or more distinct entity operations (Purpose): the sequence diagram.

## Impact

- specification repository only: `openspec/schemas/liverty-clean-arch/schema.yaml`, `scripts/check-diagrams.py` (replacing `scripts/check-story-diagrams.py`), `.pre-commit-config.yaml`, `Makefile`, `.github/workflows/ci.yml`, and the main specs listed above.
- The diagrams need Mermaid 11.15 or later (`eventmodeling`); the conventions were verified on 12.3.0. Viewers with older Mermaid show the fence source instead of the diagram.
- No backend, frontend or cloud-provisioning change. Aligning the backend's event subject names with the event names defined here is a separate change.
