# AGENTS.md
Guidance for coding agents working in this repository.

## Project Overview
- Repo: `repo-explorer`
- Language: Python `>=3.13`
- Dependency manager: `uv` (`uv.lock` present)
- Backend: FastAPI
- Frontend folder exists but is currently empty
- Current codebase is scaffold-level

Intended product behavior (small local RAG over a repo/docs folder):
1. Read local files.
2. Chunk text.
3. Embed chunks.
4. Retrieve top-k chunks.
5. Rerank candidates locally.
6. Build prompt context.
7. Return answer with file citations.

## Repository Layout
- `main.py` - minimal script entrypoint.
- `backend/app.py` - FastAPI app and `/ask` SSE scaffold.
- `backend/ai/` - AI orchestration layer (mostly empty).
- `backend/vectors/` - vector/embedding layer (mostly empty).
- `backend/api/` - schemas/models modules (mostly empty).
- `README.md` - currently empty.

Note: `backend/ai/agenets.py` appears misspelled.
If refactoring, migrate to `agents.py` carefully and update imports atomically.

## Setup and Run Commands
Run commands from repository root.

Environment setup:
- `uv sync`

Run entrypoint script:
- `uv run python main.py`

Run FastAPI app (dev):
- `uv run fastapi dev backend/app.py`

Alternative app run:
- `uv run uvicorn backend.app:app --reload`

## Build / Lint / Test Commands
There is no dedicated build/lint/test config in `pyproject.toml` yet.
Use the commands below as current baseline.

Build/sanity:
- `uv sync`
- `uv run python -m compileall backend main.py`

Lint/format (current state):
- No linter/formatter is configured.
- If tooling is introduced, prefer Ruff:
  - `uv run ruff check .`
  - `uv run ruff format .`

Tests (current state):
- No tests currently exist.
- `pytest` is not declared yet.
- Once tests are added, use:
  - all tests: `uv run pytest`
  - one file: `uv run pytest tests/test_<name>.py`
  - one test: `uv run pytest tests/test_<name>.py::test_<case>`
  - keyword: `uv run pytest -k "keyword"`

Single-test execution guidance:
- Prefer deterministic node-id form:
  - `uv run pytest path/to/test_file.py::test_function_name`
- Use `-k` only when exact node id is unknown.

## Coding Style Rules
Follow these conventions unless explicit project config is added later.

Imports:
- Group imports as: stdlib, third-party, local.
- Keep imports explicit; avoid wildcard imports.
- Avoid top-level side-effect imports unless required.

Formatting:
- Follow PEP 8.
- 4-space indentation.
- Keep lines readable (target ~88-100 chars).
- Use trailing commas in multi-line literals/calls when helpful.
- Avoid comments that restate obvious code.

Types:
- Add type hints to public functions/methods/module APIs.
- Keep annotations accurate to runtime behavior.
- Use iterator/async iterator types for streaming behavior.
- Prefer concrete types where practical.

Naming:
- Files/modules: `snake_case.py`
- Variables/functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Endpoint handlers should be intent-revealing (`ask_question`, etc.).

Error handling:
- Validate input and raise clear `HTTPException` errors for API callers.
- Do not swallow exceptions silently.
- Add context when re-raising internal exceptions.
- If answer confidence is low, state uncertainty explicitly.

Architecture boundaries:
- Keep route wiring in `backend/app.py`.
- Keep API schemas in `backend/api/schemas.py`.
- Keep AI orchestration in `backend/ai/`.
- Keep embedding/index logic in `backend/vectors/`.
- Keep heavy logic out of route handlers.

## RAG-Specific Guidance
- Always include source file paths in answers.
- Prefer retrieve + rerank over retrieve-only.
- Preserve chunk metadata (`chunk_id`, `file_path`, chunk text).
- Keep prompts constrained to retrieved context.
- Never fabricate citations.

## Suggested Stack (Aligned With Intent)
Not fully implemented yet, but appropriate for this project:
- embeddings: `sentence-transformers`
- embedding models:
  - `BAAI/bge-small-en-v1.5`
  - `all-MiniLM-L6-v2`
- vector index: `faiss-cpu`
- reranker: `BAAI/bge-reranker-base` (or smaller local equivalent)
- generation: local Ollama model or API-backed LLM

Keep dependency additions minimal and justified.

## Cursor/Copilot Rules Status
Checked these paths:
- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`

Current result: none of these rule files exist in this repository.
If added later, treat them as higher-priority instructions and update this file.

## Agent Working Agreements
- Prefer small, reviewable changes over broad rewrites.
- Preserve user-authored changes in dirty worktrees.
- Do not remove placeholder modules unless task scope requires it.
- Document any newly introduced run/test command in docs.
- When tests are introduced, include a single-test command example in notes.
