import os
from functools import lru_cache
from pathspec import PathSpec
from ..data.file import read_file_lines

@lru_cache(maxsize=128)
def get_gitignore_spec(root: str) -> PathSpec:
    """Get gitignore spec with caching to avoid redundant filesystem reads."""
    return PathSpec.from_lines(
        "gitwildmatch", [*[".gitignore", ".git/"], *scan_gitignore_files(root)]
    )


@lru_cache(maxsize=256)
def scan_gitignore_files(cwd: str = None) -> tuple[str, ...]:
    """Scan gitignore files recursively with caching. Returns tuple for hashability."""
    if cwd is None:
        cwd = os.getcwd()

    gitignore_path = os.path.join(cwd, ".gitignore")
    gitignore_lines = set()

    if os.path.isfile(gitignore_path):
        lines = read_file_lines(gitignore_path)
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                gitignore_lines.add(line)

    parent_dir = os.path.dirname(cwd)

    if parent_dir != cwd and os.path.exists(parent_dir):
        parent_gitignore_lines = scan_gitignore_files(parent_dir)
        gitignore_lines.update(parent_gitignore_lines)

    return tuple(sorted(gitignore_lines))  # Return tuple for hashability
