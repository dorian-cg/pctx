from ..data.vector import files_collection

def ask(query: str, threshold: float = 1.0) -> None:
    results = files_collection.query(query_texts=[query])

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


