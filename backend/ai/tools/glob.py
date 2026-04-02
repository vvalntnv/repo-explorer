from __future__ import annotations

from ._common import get_active_repo_root, resolve_repo_path


def glob(
    pattern: str,
    root: str = ".",
    max_results: int = 500,
) -> list[str]:
    """Return file paths matching a glob pattern under the repository."""
    if not pattern.strip():
        raise ValueError("pattern must not be empty")
    if max_results < 1:
        raise ValueError("max_results must be >= 1")

    repo_root = get_active_repo_root()

    try:
        base = resolve_repo_path(root)
    except ValueError as exc:
        raise ValueError(f"Root must stay inside repository: {root}") from exc

    if not base.exists() or not base.is_dir():
        raise FileNotFoundError(f"Root directory not found: {root}")

    results: list[str] = []
    for match in base.glob(pattern):
        if not match.is_file():
            continue
        results.append(str(match.relative_to(repo_root)))
        if len(results) >= max_results:
            break

    return sorted(results)
