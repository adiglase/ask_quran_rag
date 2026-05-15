# Ask Quran RAG

This context describes the domain language for a personal Quran RAG backend that answers English questions from retrieved Quran translation evidence.

## Language

**Translated Ayah**:
A single Quran ayah reference together with its Phase 1 English translation text.
_Avoid_: Verse row, ayah row

**Ayah Reference**:
A computed numeric Quran citation in `surah:ayah` form, such as `2:255`.
_Avoid_: Surah name citation, verse label

**Reingestion**:
A reset-and-replace import that wipes existing translated ayah and embedding rows before loading a translation dataset again.
_Avoid_: Incremental ingestion, batch replay, schema rebuild

## Relationships

- A **Translated Ayah** has exactly one **Ayah Reference**
- **Reingestion** replaces all existing **Translated Ayah** records for the active dataset
- **Reingestion** resets data rows, while migrations own table structure
- Source file checksums are not part of the Phase 1 domain model
- Phase 1 stores numeric ayah references, not surah names
- **Ayah Reference** is derived from surah number and ayah number, not stored as separate database state
- **Translated Ayah** records keep creation and update timestamps even though reingestion usually replaces rows wholesale
- Embeddings are stored separately from **Translated Ayah** records and do not track text hashes in Phase 1
- Embedding records store both provider and model names
- Phase 1 Gemini embeddings use 1536 dimensions
- Embedding dimension is enforced by the vector column type, not stored as separate row data
- Each **Translated Ayah** has at most one current embedding record
- Deleting a **Translated Ayah** deletes its embedding record
- **Translated Ayah** and embedding records use integer database identifiers
- The database enforces simple translated ayah invariants; ingestion validates full Quran completeness
- Creation and update timestamps are maintained by application code, not database triggers
- Phase 1 vector search uses an HNSW index with cosine distance

## Example dialogue

> **Dev:** "If the source file changes shape, do we migrate existing rows?"
> **Domain expert:** "No — **Reingestion** means clear the current translated ayah and embedding data, then load the dataset again."

## Flagged ambiguities

- "Ayah" was used to mean both a Quran reference and an English translation record — resolved: Phase 1 stores **Translated Ayah** records.
- "Drop the table" was used to mean resetting data — resolved: **Reingestion** wipes rows and reloads them, but does not rebuild schema.
- Checksum auditing was proposed for source integrity — rejected for Phase 1 because reingestion is manual and personal.
- `reference` was proposed as a stored column — rejected because it duplicates surah number and ayah number.
- `text_hash` was proposed for embedding consistency — rejected for Phase 1 because reingestion wipes translated ayah and embedding rows together.
- `embedding_dimension` was proposed as a stored column — rejected because `vector(1536)` already defines the dimension.
