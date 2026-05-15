# Use HNSW Cosine Vector Index

Phase 1 uses a pgvector HNSW index with cosine distance for ayah embedding retrieval. The dataset is small, HNSW avoids the training step required by IVFFlat, and cosine distance matches the semantic similarity workflow for comparing user question embeddings against stored ayah embeddings.
