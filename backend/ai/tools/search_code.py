import re
from pathlib import Path

from ._common import get_active_repo_root, is_text_like, resolve_repo_path
from .models import SearchMatch


def search_code(
    query: str,
    path: str = ".",
    file_pattern: str = "**/*",
    use_regex: bool = False,
    case_sensitive: bool = False,
    max_results: int = 100,
) -> list[SearchMatch]:
    """Search code/text files and return line-level matches."""
    if not query.strip():
        raise ValueError("query must not be empty")
    if max_results < 1:
        raise ValueError("max_results must be >= 1")

    repo_root = get_active_repo_root()

    try:
        base = resolve_repo_path(path)
    except ValueError as exc:
        raise ValueError(f"Path must stay inside repository: {path}") from exc

    if not base.exists() or not base.is_dir():
        raise FileNotFoundError(f"Directory not found: {path}")

    regex_flags = 0 if case_sensitive else re.IGNORECASE
    if use_regex:
        compiled = re.compile(query, flags=regex_flags)
    else:
        escaped = re.escape(query)
        compiled = re.compile(escaped, flags=regex_flags)

    matches: list[SearchMatch] = []
    for file_path in base.glob(file_pattern):
        if not file_path.is_file() or not is_text_like(file_path):
            continue

        rel_parts = file_path.relative_to(repo_root).parts
        if any(part.startswith(".") for part in rel_parts):
            continue

        for line_number, line in enumerate(_read_lines(file_path), start=1):
            if compiled.search(line) is None:
                continue
            matches.append(
                SearchMatch(
                    file_path=str(file_path.relative_to(repo_root)),
                    line_number=line_number,
                    line_text=line.rstrip(),
                )
            )
            if len(matches) >= max_results:
                return matches

    return matches


def _read_lines(file_path: Path) -> list[str]:
    with file_path.open("r", encoding="utf-8", errors="replace") as file:
        return file.readlines()
