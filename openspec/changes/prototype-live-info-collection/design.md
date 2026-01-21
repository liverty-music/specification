## Architecture Design: Live Information Collection

## Context

We need to extract structured live information (dates, venues) from artist websites. Building custom scrapers for every site is unscalable. We use a Generative AI approach with Gemini Grounding.

## Goals / Non-Goals

- **Goals**: Exhaustive extraction of future live events from any registered artist site.
- **Non-Goals**: Custom scraper development, real-time updates (batch processing is acceptable).

---

## Architecture (2026 Best Practice)

### Overview

Gemini's **Grounding with Vertex AI Search** eliminates manual HTML fetching. The model internally queries the DataStore and receives **Extractive Segments** (relevant text chunks) instead of raw HTML.

```
┌─────────────────────────────────────────────────────────────────┐
│                      Gemini API (Single Call)                   │
│                                                                 │
│  ┌─────────────┐    ┌──────────────────────────────────────┐   │
│  │ Prompt      │    │ VertexAISearch Grounding Tool        │   │
│  │ "Extract    │───▶│   • Queries DataStore automatically   │   │
│  │  live info  │    │   • Returns Extractive Segments      │   │
│  │  for X      │    │   • No manual HTML fetching needed   │   │
│  │  from TODAY"│    │                                      │   │
│  └─────────────┘    └──────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ResponseSchema Enforcement                              │   │
│  │   • Guarantees JSON structure                           │   │
│  │   • Required fields: artist_name, event_name, venue...  │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│      Structured JSON Output                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component        | Purpose                        | Configuration                                 |
| ---------------- | ------------------------------ | --------------------------------------------- |
| **DataStore**    | Indexes artist websites        | `createAdvancedSiteSearch: true`              |
| **TargetSite**   | Registers artist domains       | `www.{artist}.com/*` per artist               |
| **SearchEngine** | Enterprise search capabilities | `SEARCH_TIER_ENTERPRISE`, `SEARCH_ADD_ON_LLM` |
| **Gemini**       | Extracts structured data       | `VertexAISearch` tool, `ResponseSchema`       |

### Why Grounding?

1. **Token Efficiency**: Extractive Segments (~10KB) vs Raw HTML (~60KB).
2. **Reliability**: No manual fetch errors, no truncation bugs.
3. **Simplicity**: Single API call replaces Search → Fetch → Parse pipeline.

---

## Decisions

### Decision: Gemini Grounding over Manual Fetch

- **Why**: Eliminates the complexity of HTML fetching, truncation handling, and retry logic.
- **Trade-off**: Less control over exact content passed to Gemini.

### Decision: ResponseSchema for Structured Output

- **Why**: Guaranteed JSON format, prevents malformed output.
- **Configuration**: `Required` fields ensure no data omission.

### Decision: `max_extractive_segment_count: 10`

- **Why**: Tour schedules can have 30+ events. Default (5) may truncate.

---

## Risks / Trade-offs

- **Risk**: Extractive Segments may miss content buried in JavaScript.
  - **Mitigation**: `createAdvancedSiteSearch: true` enables JS rendering.
- **Risk**: Gemini hallucination.
  - **Mitigation**: `Temperature: 0`, `ResponseSchema` with strict types.

---

## Post-Processing (Go)

1.  **Filter**: Exclude past events (`Date < Now`).
    - _Note_: Prompt must include "Today is {YYYY-MM-DD}" to help Gemini, but strict filtering must be done in Go.
2.  **Deduplicate**: Remove duplicates based on `(EventName, Date, Venue)`.
3.  **Sort**: Ascending order by `Date`.
