from ..data.vector import files_collection

def find(query: str) -> None:
    results = files_collection.get(where_document={ "$contains": query })
    metadatas = results["metadatas"]
    documents = results["documents"]

    if len(metadatas) == 0:
        print("No results found.")
        return
    
    for metadata, document in zip(metadatas, documents):
        print(f"{metadata['path']}")
        print(f"({metadata['line_number']}) {document}")
