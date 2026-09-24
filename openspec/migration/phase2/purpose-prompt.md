# Purpose paragraphs for the new spec tree

Each entry in `openspec/migration/phase2/purpose-todo.json` is a new spec (`target`) assembled from one or more old specs (`sources`, with each old spec's Purpose paragraph in `source_purposes`). Write ONE Purpose paragraph per target.

Rules
- 50–400 characters, English, present tense, one paragraph, no headings, no bullets.
- Say what this capability does for its audience or what the entity/usecase is. The path tells you the layer: `stories/<story>` is a user goal; `components/entity/<e>` defines the entity; `components/usecase/<e>/<m>` is one operation; `components/adapter|infrastructure/<audience>/<web|api>/…` is that audience's surface or contract.
- Read the target's requirements in `openspec/specs.next/<target>/spec.md` so the paragraph matches what is actually there. Do not paraphrase the old Purposes blindly; several of them described a broader or narrower spec than what landed here.
- No implementation type names, no file paths, no dates, no mention of migration or of the old spec names.

Output: one file per target at `openspec/migration/phase2/output/purpose/<target with / replaced by __>.md` containing only the paragraph. Write nothing else.
