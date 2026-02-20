# Summary - Universal Data Connector

---

## Challenges Faced & Solutions

**Challenge 1: Unified interface for different data types**
The three data sources (CRM, support tickets, analytics) have completely different structures. The challenge was exposing them through a single endpoint without losing the ability to filter each one differently. I solved this with a `BaseConnector` abstract class that enforces a common `fetch(**kwargs)` interface, while each connector handles its own filtering logic internally.

**Challenge 2: Voice-optimized responses**
Voice conversations cannot handle large data dumps - an LLM reading out 50 records is unusable. I built a two-layer approach: first `apply_voice_limits` caps results to 10, then `summarize_if_large` condenses anything still too large into a single sentence. Every response also includes a `voice_summary` field that can be spoken directly.

**Challenge 3: LLM function calling schema design**
The schema exposed via `/data/schema/functions` needed to be precise enough that an LLM could call the right endpoint with the right parameters without hallucinating. I kept the parameter enums strict (e.g. status must be "open" or "closed") to reduce LLM errors.

---

## Design Decisions & Tradeoffs

**Single unified endpoint vs. separate endpoints per source**
I chose a single `/data/{source}` endpoint. This makes the LLM function schema simpler - the model only needs to learn one calling pattern. The tradeoff is that the parameter list is longer since it covers all three sources.

**Keyword routing in `/data/chat` vs. real LLM call**
The chat endpoint uses keyword matching instead of an actual OpenAI API call. This keeps the project self-contained and runnable without an API key. In production this would be replaced with a real LLM call using the `/data/schema/functions` output as the tools parameter.

**JSON files as data source**
Using flat JSON files makes the project easy to run locally with zero infrastructure. The tradeoff is it doesn't scale. The architecture is designed so connectors can be swapped - replacing `json.load()` with an async database query is a one-file change per connector.

---

## What I'd Improve With More Time

1. **Real LLM integration** - wire `/data/chat` to Claude or OpenAI with actual tool_use/function_calling, so the routing is intelligent rather than keyword-based
2. **PostgreSQL backend** - replace JSON files with async database queries for real scalability
3. **Redis caching** - cache frequent queries (e.g. "active customers") with a 60-second TTL
4. **Authentication** - add API key middleware so each tenant only sees their own data
5. **Streaming responses** - for large analytics queries, stream results back chunk by chunk
6. **Better test coverage** - add integration tests with a real test database

---

## What I Learned

- How FastAPI's automatic OpenAPI schema generation maps directly to LLM function calling schemas — the same Pydantic models that power validation also power the LLM interface
- The importance of designing for the output format first — knowing responses need to be voice-friendly shaped every decision from filtering to metadata structure
- How abstract base classes make it easy to add new data sources without touching existing code — adding a fourth connector (e.g. billing data) would require zero changes to the router or services layer
