import os
from ..data.vector import files_collection
from ..data.file import scan_child_dirs
from ..git.gitignore import get_gitignore_spec

def find(query: str) -> None:
    cwd = os.getcwd()
    child_dirs = scan_child_dirs(cwd)
    dirs = [cwd, *child_dirs]
    gitignore = get_gitignore_spec(cwd)
    not_ignored_dirs = [d for d in dirs if not gitignore.match_file(os.path.join(d, "a.b"))]
    results = files_collection.get(where_document={ "$contains": query }, where={ "dir": { "$in" : not_ignored_dirs } })
    metadatas = results["metadatas"]
    documents = results["documents"]

    if len(metadatas) == 0:
        print("No results found.")
        return
    
    for metadata, document in zip(metadatas, documents):
        print(f"{metadata['path']}")
        print(f"({metadata['line_number']}) {document}")
