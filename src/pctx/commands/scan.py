import os
from uuid import uuid4
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
            files_collection.delete(where={"path": {"$eq": path}})

            if gitignore.match_file(path):
                continue

            lines = read_file_lines(path)

            if len(lines) > 0:
                print(f"[Scanning] {path}")

                ids = []
                documents = []
                metadatas = []

                for i in range(len(lines)):
                    ids.append(str(uuid4()))
                    documents.append(lines[i].strip())
                    metadatas.append({
                        "path": path,
                        "line_number": i + 1, 
                        "dir": os.path.dirname(path)
                    })

                chunk_size = 1000
                ids_chunks = list(chunk_list(ids, chunk_size))
                documents_chunks = list(chunk_list(documents, chunk_size))
                metadatas_chunks = list(chunk_list(metadatas, chunk_size))

                for ids, documents, metadatas in zip(ids_chunks, documents_chunks, metadatas_chunks):
                    files_collection.add(ids=ids, documents=documents, metadatas=metadatas)

                print(f"[Scanned] ({len(lines)} lines)")


        if os.path.isdir(path):
            dirs.append(path)

    for dir in dirs:
        scan(dir)


def chunk_list(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]