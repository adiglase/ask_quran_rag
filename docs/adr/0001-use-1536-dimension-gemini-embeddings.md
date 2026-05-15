# Use 1536-Dimension Gemini Embeddings

Phase 1 uses Gemini embeddings at 1536 dimensions and stores them in pgvector as fixed-size vectors. Gemini recommends 1536 as one of its standard output sizes, and pgvector can index normal `vector(1536)` columns with HNSW; changing dimensions later should be treated as a deliberate migration and reindex.
