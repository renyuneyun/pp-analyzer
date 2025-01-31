Do fine-tuning for PoliAnalyzer, and evaluate the models.


1. Install dependencies using `poetry`.
2. Copy `.env.example` to `.env` and fill in the relevant fields before using this tool.
3. You may also need to create an `out/` directory under this level for caching (and fetching) data and results, if it's not automatically created.
4. Pick the desired notebook under `notebooks/`. If unsure, follow the numbers (1, 2, 3).
    - `2-9-evaluate-queue` is a specialized version for `2-evaluate-model`, to queue the evaluation jobs and result fetching. No need to use both unless intentionally necessary.
    - Results from each step is cached (in its own subdir under the `out/` dir), for use in later step(s).
    - Queries / Jobs can be submitted either as direct queries, or batch jobs.
    - Some operations will submit an async job to the server, so they need to be waited.
