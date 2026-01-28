from pathlib import Path
from chromadb import PersistentClient

client = PersistentClient(path=Path.home().joinpath(".pctx"))
files_collection = client.get_or_create_collection(name="files")