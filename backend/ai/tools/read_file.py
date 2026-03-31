from ._common import resolve_repo_path


def read_file(
    path: str,
    start_line: int = 1,
    max_lines: int = 300,
) -> str:
    """Read a text file in the repository and return line-numbered content."""
    if start_line < 1:
        raise ValueError("start_line must be >= 1")
    if max_lines < 1:
        raise ValueError("max_lines must be >= 1")

    try:
        resolved_path = resolve_repo_path(path)
    except ValueError as exc:
        raise ValueError(f"Path must stay inside repository: {path}") from exc

    if not resolved_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not resolved_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {path}")

    with resolved_path.open("r", encoding="utf-8", errors="replace") as file:
        lines = file.readlines()

    start_idx = start_line - 1
    chunk = lines[start_idx : start_idx + max_lines]
    if not chunk:
        return ""

    rendered_lines = []
    for index, line in enumerate(chunk, start=start_line):
        rendered_lines.append(f"{index}: {line.rstrip()}")

    return "\n".join(rendered_lines)
