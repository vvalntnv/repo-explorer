from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".js",
    ".ts",
    ".tsx",
    ".rs",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
}


def resolve_repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    resolved = candidate.resolve()
    resolved.relative_to(REPO_ROOT)
    return resolved


def is_text_like(path: Path) -> bool:
    if path.suffix.lower() in DEFAULT_TEXT_EXTENSIONS:
        return True
    return path.suffix == ""
