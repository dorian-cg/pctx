import os
from ..data.vector import files_collection
from ..data.file import scan_child_dirs
from ..git.gitignore import get_gitignore_spec

def ask(query: str, threshold: float = 1.0) -> None:
    cwd = os.getcwd()
    child_dirs = scan_child_dirs(cwd)
    dirs = [cwd, *child_dirs]
    gitignore = get_gitignore_spec(cwd)
    not_ignored_dirs = [d for d in dirs if not gitignore.match_file(os.path.join(d, "a.b"))]
    results = files_collection.query(query_texts=[query], where={ "dir": { "$in" : not_ignored_dirs }})

    if len(results["documents"]) == 0 or len(results["documents"][0]) == 0:
        print("No results found.")
        return
    
    distances = results["distances"][0]

    for i, distance in enumerate(distances):
        if distance <= threshold:
            doc = results["documents"][0][i]
            meta = results["metadatas"][0][i]
            print(f"{meta['path']} at line {meta['line_number']}:")
            print(doc)


