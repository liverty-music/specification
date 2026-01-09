## 1. Implementation
- [ ] 1.1 Define Proto messages for `ScrapedEvent` (output) in `entity/intel/v1` <!-- id: 0 -->
- [ ] 1.2 (Infra) Manually create Vertex AI Search Data Store for `https://www.uverworld.jp/` <!-- id: 1 -->
- [ ] 1.3 (Backend) Implement `VertexAISearchClient` (Go) to query the specific data store <!-- id: 2 -->
- [ ] 1.4 (Backend) Implement `GeminiParser` (Go) using `gemini-2.5-flash` <!-- id: 3 -->
- [ ] 1.5 (Backend) Create a CLI tool to run the flow and log results to stdout <!-- id: 4 -->
- [ ] 1.6 (Verification) Verify output accuracy for UVERworld 2025 live schedule <!-- id: 5 -->
