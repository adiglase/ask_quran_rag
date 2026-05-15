# Answer Boundary Policy

This project is a personal Quran RAG application. Phase 1 answers questions from an indexed English Quran translation only.

See `docs/grounding-policy.md` for the strict workflow, sufficiency states, and citation validation rules.

## Source Boundary

- Use retrieved English Quran translation ayat as the only answer evidence.
- Do not use tafsir, hadith, scholar opinions, fiqh material, historical background, or model-only religious knowledge in Phase 1 answers.
- Always attempt retrieval before deciding whether a question can be answered.
- The model must not answer from general knowledge when retrieved ayat do not clearly support the response.

## Question Handling

- Accept natural user wording, including broad questions like "what does Islam say about patience?"
- Internally narrow broad wording to the indexed Quran evidence.
- Answer with evidence-bounded wording such as "the retrieved ayat support..." instead of claiming to represent all Islamic doctrine.
- Normative or action questions are allowed, but only when retrieved ayat directly support the response.
- If a complete ruling would require sources outside the retrieved Quran translation, return a limited answer or insufficient-evidence response.

## Answer Style

- The model may cautiously synthesize across retrieved ayat when every claim is directly supported by cited evidence.
- Prefer concise summaries with citations.
- Short direct quotes from retrieved translation text are allowed when useful.
- Return the full retrieved evidence separately from the generated answer so the answer does not need to repeat long ayat.
- Mention non-fatwa or evidence-boundary language only when the user asks for a ruling or when the evidence does not establish the requested conclusion.

## Evidence and Citations

- Phase 1 evidence is English translation text only.
- Citations must use exact surah and ayah references, such as `2:255`.
- Every generated answer must cite the retrieved ayat that support it.
- Citation validation must reject citations that are not present in the retrieved evidence set.

## Grounding Status

Every answer workflow must end with one of these grounding states:

- `grounded`: retrieved ayat clearly support the answer.
- `partial`: retrieved ayat support only part of the answer, or support a cautious limited answer.
- `insufficient_evidence`: retrieved ayat do not clearly support an answer.

When the status is `partial` or `insufficient_evidence`, the response should clearly identify the evidence limit instead of filling the gap with model opinion.
