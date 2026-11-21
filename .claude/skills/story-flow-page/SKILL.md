---
name: story-flow-page
description: Turn one user story spec (openspec/specs/stories/<id>) into a Japanese HTML page of diagrams that a person can review without reading the spec's English - who can do what, one sequence diagram per scene, the entity's state transitions, the rules that always hold, and a map from each spec scenario to its place on the page. Use when the user asks to see, review, explain or diagram a story's flow or business logic (ストーリーを図にして, フローを見せて, フローチャートで確認したい, このストーリーの分岐を図で, track-ticket-journey の図), or wants the same kind of page for another story. Not for a design proposal before a spec exists (html-plan) or a single diagram in a PR (mermaid-diagrams alone).
---

# Story flow page

The page answers one question for its reader: "when a person does X in the app, what does the app save, and what appears on which screen?" The reader is the product owner or a reviewer. They know the product but have not read the spec's English, the entity specs or the code, and they open sections in any order. Every rule below follows from that.

The first page made this way is `stories/track-ticket-journey` (published as an Artifact on 2026-11-22). The quality bar it set: every label uses a name the spec defines, every sentence and diagram label says who does what, every section says what situation it is about before it shows anything, and every diagram was looked at in both colour schemes.

Load these skills before writing, and follow them: `writing:clear-prose` (every sentence, label and table cell, including its "Names and sentences" and "Documents with sections" parts), `mermaid-diagrams` (diagram type, official syntax, render check), and `artifact-design` when the page is published as an Artifact.

## 1. Gather the sources

Read, in this order, and keep the paths for the source note at the end of the page:

1. The story: `openspec/specs/stories/<id>/spec.md`. Its requirements and scenarios are the content of the page.
2. Every entity it names: `openspec/specs/components/entity/<entity>/spec.md`. The entity's attribute table and its states are the page's vocabulary.
3. Every screen or component it names: `openspec/specs/components/infrastructure/**/<component>/spec.md`. The quoted UI strings (「…」) come from here.
4. Open changes that touch these specs: `grep -rl "<id>\|<component>" openspec/changes/*/specs`. A merged change not yet archived is part of the current behaviour; say on the page which change it is.
5. Where the spec leaves the order of steps or who performs a step open (which side saves a record after sign-up, whether something happens per device or per item), read the implementing code in the `frontend` or `backend` checkout and cite it. Do not fill a gap with a plausible guess. When the sources contradict each other, record it for part 11 of the outline.

## 2. Build the vocabulary before drawing

Make the glossary first; the diagrams then use only its names.

- Entities, attributes and states keep the spec's English names (`TicketJourney`, `status`, `Tracking`). Screens keep the names the specs use (`concert sheet`, `Timetable`, `My Artists`).
- A thing the spec has no name for but the page needs (the top button of a sheet) gets one plain descriptive name, defined in the glossary, used the same way everywhere.
- Absence is not a state. If the entity spec says the record has one of N states, "no record" is written as "<Entity> なし", not as an extra state.
- Quote UI strings exactly as the component spec gives them, in 「」. Check meaning against the entity spec (Lost covers both a lost lottery and a missed payment deadline, for example) so the glossary does not narrow it.

## 3. Page outline

Use `assets/page-template.html` (CSS tokens for both themes, and the script that draws every diagram once per theme). Fill the `<main>` with these parts, in this order:

1. **Header**: the story id, a title, and one paragraph on what the page lets the reader check, and that the spec wins when the two disagree.
2. **このストーリーが決めていること**: what the user is trying to get done, what the app keeps for them (the entity, in one sentence), and what the story decides about it.
3. **このページで使う名前**: the glossary table (name, what it is), and a second table for the entity's states with their meaning and the UI label of each.
4. **図の読み方**: one paragraph on the notation the page uses (for sequence diagrams: participants left to right, numbered steps top to bottom, `alt` is one-of branches, `opt` happens only under its condition).
5. **1. 誰がどの操作をできるか**: a `usecase-beta` diagram of each kind of user (guest, signed-in fan, organizer member…) and the operations they can perform. Use `«extend»` for an operation that joins only under a condition, and say so under the diagram.
6. **One section per scene**: a scene is one situation that starts a flow: a user's action (pressing a button, signing up from a prompt, adding to a calendar) or a system trigger (a daily job, an incoming webhook, a delivery the system starts for each user). Group the story's requirements by scene, not one section per requirement. Each gets a `sequenceDiagram`. When the system starts the flow, say in the context sentence what starts it and when (「毎日 21:00 に…」).
7. **The entity's transitions**: a `stateDiagram-v2` of the states and the actions that move between them, for the entity whose state this story changes. When another story owns those transitions (this story only reads the state), do not redraw them: link that story's page or spec in part 10. Say whether the arrows are all allowed moves or only the typical ones, and name the exceptions. Skip this part when the story changes no state.
8. **どの場面でも成り立つ規則**: requirements that are not one flow (loading, consistency across screens, sign-out), as a list, with one sentence on why they are not drawn.
9. **spec のシナリオがこのページのどこにあるか**: a table, every scenario heading of the story (in English, as written) to the diagram and step number or branch name where it appears. A scenario with no place on the page is a gap: add it, or list it in the next part with the reason.
10. **このページに入れていないもの**: related behaviour that other specs decide, each with the spec or story that owns it.
11. **spec の食い違い** (only when there is one): where two specs, or a spec and the code, disagree on something the page draws. For each: what each source says (path, and file:line for code), which one the page draws (the story, unless the user says otherwise), and what a reader sees in the app today. Mark the step in the diagram with a note that points here. Tell the user about each one in the report as well; a conflict is a finding, not a footnote.
12. **Source note**: the spec paths, the `specification` commit SHA or date, open changes included, and the Mermaid version.

Every section with a diagram (parts 5 to 7) opens the same way; the parts after it have no diagram, but still open with one sentence on what they hold and why:

- **Context** (one or two sentences): who is in which situation and why it matters, then what the diagram shows.
- **この図で確かめること**: three or four claims, each with its condition, each traceable to a requirement or scenario.
- **The diagram.**

## 4. Write the diagrams

Choose and write each type with the `mermaid-diagrams` skill (official syntax page, pinned version, its defaults for `layout` and `look`). On top of that skill:

- **Participants** are the user (`actor`), the screens or dialogs that act (grouped in a `box` for the app), outside services by name (Zitadel, the calendar app, the browser's push service), and the backend. Name a backend participant by the entities it stores; when the story's flow is carried by backend use cases (a job that discovers, a use case that announces, one that delivers), make each use case a participant of type `control`, named as the spec names it (「配信（Deliver）」), and keep the stores as `database` participants.
- **Every message and note is a sentence with a subject**: 「ゲストが通知ボタンを押す」, 「アプリが status = Tracking、status set by = fan で保存する」, 「backend がエラーを返す」. An arrow's direction does not replace the subject.
- **Show who sets a value** when the entity records it (`status set by = fan` or `inference`), and what the user sees when a save fails.
- **Branches**: `alt` for outcomes the user or the system chooses between (success / failure, guest / signed in), `opt` for a step that happens only under a condition. Write each condition as a sentence too.
- **No emoji in diagram labels**; a renderer without an emoji font draws an empty box. Emoji may stay in the HTML tables.
- **Line length**: break a label before it overflows its box: `<br/>` in sequence and state diagrams; in `usecase-beta`, where `<br/>` prints as text, a real line break inside a Markdown string label. A sentence with its subject often needs two lines; that is fine. A note that needs more than four lines holds two points: split it, or move one into the section's list.
- **Size**: split a sequence diagram that grows past about 20 steps into two scenes.

Work in one directory in the scratchpad: one `<name>.mmd` file per diagram and `main.html` with the inside of `<main>` (start from the skeleton in `assets/page-template.html`), where each diagram's place is `<pre class="diagram">{{DIAGRAM:<name>}}</pre>`. Render each `.mmd` with `mmdc` as the mermaid skill says, then assemble the page with `python3 <this skill>/scripts/build.py <work-dir> <out.html> "<title>"`. After any edit, change the `.mmd` or `main.html` and build again; never patch the built page (escaped text breaks easily, and a `sed` replacement containing `&` inserts the matched text).

## 5. Check the page

A page counts as checked only after these, and the report to the user says which ran:

1. `mmdc` renders every `.mmd` file without a parse error.
2. `scripts/shoot.mjs` draws every diagram in the browser and takes screenshots in light, dark, and light switched to dark after load. Run it from the frontend checkout, where `playwright` is installed: `cd <frontend> && node <this skill>/scripts/shoot.mjs <page.html> <out-dir>`. It exits non-zero when a diagram failed to draw.
3. Open the screenshots and read them: every label legible against its background, no text past its box. Fix and repeat.
4. Read the page text alone, top to bottom, as the reader: each section says what situation it is about before the diagram; no word stands in for a defined name; every sentence and label has a subject; every claim matches the spec text it came from.
5. The scenario table covers every scenario of the story.

## 6. Publish

In a session with the Artifact tool, publish the page as an Artifact (private by default) and give the user the link; otherwise write it to the scratchpad and give the full path. Keep the `.mmd` files next to it so a later edit starts from them. When the user asks for changes, edit the `.mmd` files or `main.html`, build again, and publish to the same URL.
