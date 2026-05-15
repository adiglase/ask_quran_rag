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
A reset-and-replace import that wipes existing translated ayah rows before loading a translation dataset again.
_Avoid_: Incremental ingestion, batch replay, schema rebuild

**Embedding Generation**:
A separate process that creates vector embeddings for stored translated ayat.
_Avoid_: Ingestion, import

**Source Column Mapping**:
The interactive user-provided mapping from a SQLite translation source to surah number, ayah number, and translation text fields.
_Avoid_: Fixed source schema, hard-coded translation table

## Relationships

- A **Translated Ayah** has exactly one **Ayah Reference**
- **Reingestion** replaces all existing **Translated Ayah** records for the active dataset but does not generate embeddings
- **Reingestion** removes existing embedding records indirectly when it replaces **Translated Ayah** records
- **Reingestion** uses a **Source Column Mapping** to read SQLite sources with different table shapes
- **Source Column Mapping** ignores source reference columns such as `ayah_key`; **Ayah Reference** is derived after import
- **Reingestion** resets data rows, while migrations own table structure
- Source file checksums are not part of the Phase 1 domain model
- **Reingestion** performs minimal mapped-field checks but does not validate Quran completeness
- **Reingestion** imports every row from the mapped SQLite table
- **Reingestion** replaces rows atomically; failed inserts keep the previous active dataset intact
- Phase 1 stores numeric ayah references, not surah names
- **Ayah Reference** is derived from surah number and ayah number, not stored as separate database state
- **Translated Ayah** records keep creation and update timestamps even though reingestion usually replaces rows wholesale
- Embeddings are stored separately from **Translated Ayah** records and do not track text hashes in Phase 1
- **Embedding Generation** runs after **Reingestion** and fills missing embedding records for stored **Translated Ayah** records
- Successful **Reingestion** leaves embeddings absent until **Embedding Generation** is run
- Embedding records store both provider and model names
- Phase 1 Gemini embeddings use 1536 dimensions
- Embedding dimension is enforced by the vector column type, not stored as separate row data
- Each **Translated Ayah** has at most one current embedding record
- Deleting a **Translated Ayah** deletes its embedding record
- **Translated Ayah** and embedding records use integer database identifiers
- The database enforces simple translated ayah invariants; Phase 1 reingestion trusts the chosen SQLite dataset
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
- `text_hash` was proposed for embedding consistency — rejected for Phase 1 because embedding freshness is handled operationally, not by stored text hashes.
- `embedding_dimension` was proposed as a stored column — rejected because `vector(1536)` already defines the dimension.
- Full Quran completeness validation during ingestion was proposed — rejected for Phase 1; reingestion only performs minimal mapped-field checks.
- Combining translated ayah import and embedding creation in one ingestion process was proposed — rejected because **Reingestion** and **Embedding Generation** are separate Phase 1 operations.
- A fixed SQLite source schema was assumed — rejected because **Reingestion** should accept a **Source Column Mapping** for different SQLite translation sources.
- Filtering source rows during reingestion was proposed — rejected for Phase 1 because the selected table is treated as the active translation dataset.
