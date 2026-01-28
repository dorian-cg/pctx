import os
from pathspec import PathSpec
from ..data.vector import files_collection

def scan(cwd: str = None) -> list[str]:
    if cwd is None:
        cwd = os.getcwd()

    gitignore = PathSpec.from_lines(
        "gitwildmatch", [*[".gitignore", ".git/"], *scan_gitignore_files(cwd)]
    )

    ls = os.listdir(cwd)
    dirs = []

    for item in ls:
        path = os.path.join(cwd, item)

        if os.path.isfile(path):
            if gitignore.match_file(path):
                continue

            lines = read_file_lines(path)

            if len(lines) > 0:
                print(f"[Scanning] {path}")

                files_collection.delete(where={"path": {"$eq": path}})

                ids = []
                documents = []
                metadatas = []

                for i in range(len(lines)):
                    ids.append(f"{path}::line::{i+1}")
                    documents.append(lines[i])
                    metadatas.append({"path": path, "line_number": i + 1})

                files_collection.add(ids=ids, documents=documents, metadatas=metadatas)

        if os.path.isdir(path):
            dirs.append(path)

    for dir in dirs:
        scan(dir)


def read_file_lines(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []


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
