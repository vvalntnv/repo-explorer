from ._common import get_active_repo_root, resolve_repo_path


def list_files(
    path: str = ".",
    recursive: bool = True,
    include_hidden: bool = False,
    max_results: int = 500,
) -> list[str]:
    """List files in a repository path."""
    if max_results < 1:
        raise ValueError("max_results must be >= 1")

    repo_root = get_active_repo_root()

    try:
        base = resolve_repo_path(path)
    except ValueError as exc:
        raise ValueError(f"Path must stay inside repository: {path}") from exc

    if not base.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    if base.is_file():
        return [str(base.relative_to(repo_root))]

    if recursive:
        iterator = base.rglob("*")
    else:
        iterator = base.iterdir()

    results: list[str] = []
    for item in iterator:
        if not item.is_file():
            continue

        rel_parts = item.relative_to(repo_root).parts
        if not include_hidden and any(part.startswith(".") for part in rel_parts):
            continue

        results.append(str(item.relative_to(repo_root)))
        if len(results) >= max_results:
            break

    return sorted(results)
