# Agent Instructions

## Project Goal

Build a backend-first Quran RAG application for personal use. Users ask questions in English, the backend retrieves relevant Quran ayat from an indexed English translation, and the AI answers only from retrieved Quran evidence with citations.

Frontend work is deferred until the backend API is stable.

## Current Backend Direction

- Use Python with FastAPI.
- Use PostgreSQL as the canonical relational database.
- Use PostgreSQL with pgvector for vector storage and similarity search.
- Use SQLAlchemy and Alembic for database models and migrations.
- Use `uv` for Python dependency and command management.
- Use LangChain for model, embedding, retriever, and prompt building blocks.
- Use LangGraph for the explicit answer workflow.
- Use local PostgreSQL first during backend development.
- Defer Docker Compose until personal deployment readiness.
- Use OpenAI as the initial LLM provider.
- Use Gemini as the initial embedding provider with 1536-dimensional embeddings.
- Configure AI provider model names through environment variables; do not hardcode model choices.

## Current Project State

- Phase 0 foundation decisions are complete.
- Phase 1 backend scaffold is complete.
- The current active roadmap phase is Phase 2: data model and storage.
- A minimal FastAPI app, typed Pydantic settings, SQLAlchemy database configuration, Alembic setup, and initial pgvector extension migration exist.
- Local development currently targets PostgreSQL 18 with pgvector installed at the server level and enabled by migration.
- Defer database, migration, retrieval, LangChain, LangGraph, and AI provider packages until the implementation step that needs them, unless they already exist in the project.
- Follow `CONTEXT.md` for current domain language and resolved terminology.

## Product Constraints

- This is a personal project, not a public production service.
- Phase 1 is English-only.
- Phase 1 is Quran ayat only.
- Do not include tafsir, hadith, scholar opinions, or general religious claims in the answer flow unless a future phase explicitly adds those as separate source types.
- Follow the Phase 1 answer boundary in `docs/answer-boundary.md`.
- Follow the strict grounding workflow in `docs/grounding-policy.md`.
- The backend must refuse or return an insufficient-evidence response when retrieved ayat do not clearly support an answer.
- Do not let the model answer from general knowledge when Quran evidence is missing.
- Every generated answer must be grounded in retrieved ayat.
- Citations must refer to exact ayah references, such as `2:255`.
- Citation validation must ensure the model only cites ayat present in retrieved evidence.

## Data and Attribution

- Use `en-sahih-international-simple.db` as the canonical Phase 1 personal-project translation dataset.
- Attribute the translation as Saheeh International / Sahih International wherever translation source metadata is shown.
- Do not add checksum auditing in Phase 1 unless the project direction changes.

## Storage Boundaries

- PostgreSQL is the source of truth for translated ayah records, embeddings, query logs, and future application data.
- pgvector stores embedding vectors alongside canonical ayah records or in closely related embedding tables.
- Embedding rows should include enough metadata to identify the embedding provider and embedding model.

## Ingestion

- Build ingestion as a CLI first, not an API.
- Reingestion is a reset-and-replace operation: wipe existing translated ayah and embedding rows, then load the dataset again.
- The first vector indexing strategy should be one point per ayah unless evaluation shows that multi-ayah chunks are needed.
- Retrieval behavior should use pgvector similarity search, not static data lookup.

## API Expectations

- The first core endpoint is expected to be `POST /ask`.
- The exact response shape is deferred, but it should include structured answer text, citations, retrieved evidence, translation source, and grounding status.
- Add read-only Quran browsing endpoints after the core ask flow exists.
- Add rate limiting before sharing beyond local personal use to control provider cost and abuse.

## Roadmap

- Keep `roadmap.html` updated as work is completed.
- Mark roadmap tasks done only after the implementation and relevant verification are complete.
