# Strict Grounding Policy

Phase 1 answers must be grounded in retrieved English Quran translation evidence. Retrieval is mandatory for every user question.

## Required Workflow

1. Receive the user question.
2. Retrieve candidate ayat from the indexed translation source.
3. Build the evidence set from retrieved ayat only.
4. Decide evidence sufficiency before answer generation.
5. Generate an answer only from the evidence set.
6. Validate every citation against the evidence set.
7. Return the final answer, grounding status, citations, retrieved evidence, and translation source metadata.

## Evidence Sufficiency

Use these statuses:

- `grounded`: the retrieved ayat clearly support the answer.
- `partial`: the retrieved ayat support only part of the requested answer or only a cautious limited answer.
- `insufficient_evidence`: the retrieved ayat do not clearly support an answer.

The system must return `insufficient_evidence` when retrieval produces no evidence, weakly related evidence, or evidence that does not answer the question.

The system may return `partial` when retrieved ayat support a limited answer but do not establish the full answer requested by the user.

## Generation Rules

- Do not answer before retrieval.
- Do not introduce facts, rulings, historical context, tafsir, hadith, or scholar opinions that are absent from retrieved evidence.
- Do not let the model use general religious knowledge to fill gaps.
- Prefer wording like "the retrieved ayat support..." to keep the answer evidence-bounded.
- For normative questions, answer only what the retrieved ayat establish.
- If the user asks for a complete ruling and the retrieved ayat do not establish one, say the indexed Quran evidence is insufficient for that full ruling.

## Citation Rules

- Citations must use exact references such as `2:255`.
- Every cited reference must exist in the retrieved evidence set.
- Every material answer claim must be supported by at least one cited retrieved ayah.
- If citation validation fails, the response must be rejected, repaired from the same evidence set, or downgraded to `insufficient_evidence`.

## Response Requirements

Every response from the answer workflow should include:

- `answer`: the generated answer text or an insufficient-evidence message.
- `grounding_status`: one of `grounded`, `partial`, or `insufficient_evidence`.
- `citations`: exact ayah references used by the answer.
- `evidence`: retrieved ayat shown separately from the generated answer.
- `translation_source`: source metadata for the indexed translation.

