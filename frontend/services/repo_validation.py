from pathlib import Path


def is_git_repository(path: Path) -> bool:
    return path.is_dir() and (path / ".git").is_dir()
