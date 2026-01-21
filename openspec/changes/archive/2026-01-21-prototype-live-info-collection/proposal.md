# Prototype Live Info Collection

## Background
As outlined in `docs/product-design.md`, the core value proposition of Liverty Music depends on the automated collection of live information (concerts, tickets). We need to validate the technical feasibility and quality of using Google Cloud Vertex AI Search for crawling and Gemini 1.5 Pro for parsing.

## Goal
Validate the core "Search -> Parse" functionality with a simplified vertical prototype.
Target:
- **Artist**: UVERworld
- **Source**: `https://www.uverworld.jp/`
- **Output**: JSON log of search results and parsed live/ticket entities. (No DB storage).

## Scope
- **Backend**: Add a CLI tool `prototype-cli` (Go).
- **Infra**: Provision Vertex AI Search Data Store (Website) for `uverworld.jp` (Manual or Terraform).
- **Logic**:
    1.  Query Vertex AI Search for "UVERworld live schedule".
    2.  Feed results to Gemini 2.5 Flash to parse into JSON.
    3.  Print JSON to stdout.

## References & Justification
- **Vertex AI Search**: Used for "Advanced Website Indexing" to crawl and index dynamic content without building a custom scraper.
    - [GCP: Create a search data store](https://cloud.google.com/generative-ai-app-builder/docs/create-data-store-es)
- **Gemini 2.5 Flash**: Selected as a cost-effective, high-performance model sufficient for parsing search results into JSON.
    - [GCP: Gemini models list](https://cloud.google.com/vertex-ai/generative-ai/docs/models?hl=ja)

## Risks
- **Vertex AI Search Latency**: Indexing time for new sites.
- **Accuracy**: Need to verify if Flash's reasoning is sufficient for complex HTML structures compared to Pro.
