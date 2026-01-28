import os

from ..data.vector import files_collection
from ..data.file import read_file_lines
from ..git.gitignore import get_gitignore_spec

def scan(cwd: str = None) -> list[str]:
    if cwd is None:
        cwd = os.getcwd()

    gitignore = get_gitignore_spec(cwd)

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
                    metadatas.append({
                        "path": path, 
                        "line_number": i + 1, 
                        "dir": os.path.dirname(path)
                    })

                files_collection.add(ids=ids, documents=documents, metadatas=metadatas)

        if os.path.isdir(path):
            dirs.append(path)

    for dir in dirs:
        scan(dir)


