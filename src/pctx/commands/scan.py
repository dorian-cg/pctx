import os
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Iterator
from ..data.vector import files_collection
from ..data.file import read_file_lines
from ..git.gitignore import get_gitignore_spec

# Configuration constants
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB limit
CHUNK_SIZE = 5000  # ChromaDB insert limit

# Dynamically set thread pool size based on available CPU cores
# Use min(32, cpu_count + 4) for I/O-bound operations (recommended by Python docs)
_cpu_count = os.cpu_count() or 4  # Fallback to 4 if cpu_count returns None
THREAD_POOL_SIZE = min(32, _cpu_count + 4)  # Optimal for I/O-bound file operations

GITIGNORE_CACHE: dict = {}

def scan(cwd: str = None, max_lines: int = 10000) -> list[str]:
    """Optimized recursive directory scanner with parallel file processing.
    
    Args:
        cwd: Directory to scan (defaults to current working directory)
        max_lines: Maximum number of lines to process per file (default: 10000)
    """
    if cwd is None:
        cwd = os.getcwd()
    
    # Get or compute gitignore spec for this directory with caching
    if cwd not in GITIGNORE_CACHE:
        GITIGNORE_CACHE[cwd] = get_gitignore_spec(cwd)
    gitignore = GITIGNORE_CACHE[cwd]
    
    # Phase 1: Collect all file paths using os.scandir (faster than listdir)
    files_to_process = []
    subdirs = []
    
    try:
        with os.scandir(cwd) as entries:
            for entry in entries:
                try:
                    if entry.is_file(follow_symlinks=False):
                        path = entry.path
                        
                        # Early filtering: gitignore check
                        if gitignore.match_file(path):
                            continue
                        
                        # Early filtering: file size check
                        stat = entry.stat(follow_symlinks=False)
                        if stat.st_size == 0 or stat.st_size > MAX_FILE_SIZE:
                            continue
                        
                        files_to_process.append(path)
                    
                    elif entry.is_dir(follow_symlinks=False):
                        subdirs.append(entry.path)
                except (PermissionError, OSError):
                    # Skip files/dirs we can't access
                    continue
    except (PermissionError, OSError):
        # Can't access this directory
        return []
    
    # Phase 2: Bulk delete existing entries for this directory
    if files_to_process:
        try:
            files_collection.delete(where={"dir": {"$eq": cwd}})
        except Exception as e:
            print(f"[Warning] Failed to delete existing entries for {cwd}: {e}")
    
    # Phase 3: Parallel file processing with thread pool
    if files_to_process:
        all_ids = []
        all_documents = []
        all_metadatas = []
        files_processed = 0
        
        with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
            # Submit all file reading tasks
            future_to_path = {
                executor.submit(process_file, path, max_lines): path 
                for path in files_to_process
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    if result:
                        ids, documents, metadatas = result
                        all_ids.extend(ids)
                        all_documents.extend(documents)
                        all_metadatas.extend(metadatas)
                        files_processed += 1
                        
                        # Progress update every 10 files
                        if files_processed % 10 == 0:
                            print(f"[Progress] Processed {files_processed}/{len(files_to_process)} files...")
                except Exception as e:
                    print(f"[Error] Failed to process {path}: {e}")
        
        # Phase 4: Batch insert all collected data
        if all_ids:
            print(f"[Inserting] {len(all_ids)} lines from {files_processed} files...")
            insert_batched(all_ids, all_documents, all_metadatas)
            print(f"[Completed] {cwd}")
    
    # Phase 5: Recursively process subdirectories (sequential to avoid too much parallelism)
    for subdir in subdirs:
        scan(subdir, max_lines=max_lines)
    
    return []


def is_binary_file(path: str) -> bool:
    """Fast binary file detection by checking first 8KB for null bytes."""
    try:
        with open(path, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except Exception:
        return True  # Treat unreadable files as binary


def process_file(path: str, max_lines: int) -> Optional[tuple[list[str], list[str], list[dict]]]:
    """Process a single file and return (ids, documents, metadatas) or None.
    
    Args:
        path: Path to the file to process
        max_lines: Maximum number of lines to process (skip files exceeding this)
    """
    # Binary file check
    if is_binary_file(path):
        return None
    
    # Read file lines
    lines = read_file_lines(path)
    if not lines:
        return None
    
    # Skip files exceeding line limit
    if len(lines) > max_lines:
        return None
    
    # Prepare data for ChromaDB
    ids = []
    documents = []
    metadatas = []
    dir_path = os.path.dirname(path)
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped:  # Skip empty lines
            ids.append(str(uuid4()))
            documents.append(stripped)
            metadatas.append({
                "path": path,
                "line_number": i + 1,
                "dir": dir_path
            })
    
    return (ids, documents, metadatas) if ids else None


def insert_batched(ids: list[str], documents: list[str], metadatas: list[dict]) -> None:
    """Insert data into ChromaDB in optimized batches."""
    for ids_chunk, docs_chunk, meta_chunk in zip(
        chunk_list(ids, CHUNK_SIZE),
        chunk_list(documents, CHUNK_SIZE),
        chunk_list(metadatas, CHUNK_SIZE)
    ):
        try:
            files_collection.add(
                ids=list(ids_chunk),
                documents=list(docs_chunk),
                metadatas=list(meta_chunk)
            )
        except Exception as e:
            print(f"[Error] ChromaDB insert failed: {e}")


def chunk_list(data: list, size: int) -> Iterator[list]:
    """Split list into chunks of specified size."""
    for i in range(0, len(data), size):
        yield data[i:i + size]