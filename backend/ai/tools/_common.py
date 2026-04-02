from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from pathlib import Path

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[3]
_active_repo_root: ContextVar[Path] = ContextVar(
    "active_repo_root",
    default=DEFAULT_REPO_ROOT,
)

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


def get_active_repo_root() -> Path:
    return _active_repo_root.get()


@contextmanager
def use_repo_root(path: str | Path):
    resolved_root = Path(path).expanduser().resolve()
    if not resolved_root.exists() or not resolved_root.is_dir():
        raise FileNotFoundError(f"Directory not found: {path}")

    token: Token[Path] = _active_repo_root.set(resolved_root)
    try:
        yield resolved_root
    finally:
        _active_repo_root.reset(token)


def resolve_repo_path(path: str | Path) -> Path:
    active_root = get_active_repo_root()
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = active_root / candidate

    resolved = candidate.resolve()
    resolved.relative_to(active_root)
    return resolved


def is_text_like(path: Path) -> bool:
    if path.suffix.lower() in DEFAULT_TEXT_EXTENSIONS:
        return True
    return path.suffix == ""
