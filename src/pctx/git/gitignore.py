import os
from pathspec import PathSpec
from ..data.file import read_file_lines

def get_gitignore_spec(root: str) -> PathSpec:
    return PathSpec.from_lines(
        "gitwildmatch", [*[".gitignore", ".git/"], *scan_gitignore_files(root)]
    )


def scan_gitignore_files(cwd: str = None) -> list[str]:
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

    return list(gitignore_lines)
