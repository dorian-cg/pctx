import os

def read_file_lines(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []

def scan_child_dirs(root: str) -> None:
    dirs = []
    ls = os.listdir(root)

    for item in ls:
        path = os.path.join(root, item)

        if os.path.isdir(path):
            dirs.append(path)
            dirs.extend(scan_child_dirs(path))

    return dirs
