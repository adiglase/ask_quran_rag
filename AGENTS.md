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
- Use OpenAI as the initial LLM and embedding provider.
- Configure OpenAI model names through environment variables; do not hardcode model choices.

## Current Project State

- Phase 0 foundation decisions are complete.
- Phase 1 backend scaffold is complete.
- The current active roadmap phase is Phase 2: data model and storage.
- A minimal FastAPI app, typed Pydantic settings, SQLAlchemy database configuration, Alembic setup, and initial pgvector extension migration exist.
- Local development currently targets PostgreSQL 18 with pgvector installed at the server level and enabled by migration.
- Defer database, migration, retrieval, LangChain, LangGraph, and OpenAI packages until the implementation step that needs them, unless they already exist in the project.

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
- The accepted dataset checksum is `1ade0edcc1346405227db43d0b253949dbc78ecb8becf9c46af97de8552a7772`.
- Attribute the translation as Saheeh International / Sahih International wherever translation source metadata is shown.
- Store translation records with source metadata and file checksums so the dataset can be audited or swapped later.

## Storage Boundaries

- PostgreSQL is the source of truth for Quran metadata, translation records, embeddings, ingestion batches, query logs, and future application data.
- pgvector stores embedding vectors alongside canonical ayah records or in closely related embedding tables.
- Embedding rows should include enough metadata to audit source version, embedding provider, embedding model, text hash, and ingestion batch.

## Ingestion

- Build ingestion as a CLI first, not an API.
- Ingestion should be idempotent and support dry runs, reindexing, source version changes, and failure recovery.
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
