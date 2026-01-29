import os

def read_file_lines(path: str) -> list[str]:
    """Read file lines with better error handling and memory efficiency."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            # For large files, this is still efficient as Python buffers I/O
            # Using list() instead of readlines() allows iteration optimization
            return list(f)
    except (OSError, UnicodeDecodeError, PermissionError):
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
