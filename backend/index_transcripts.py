
from pathlib import Path
import hashlib

import chromadb
import httpx


PROJECT_DIR = Path(__file__).resolve().parent.parent
TRANSCRIPT_DIR = PROJECT_DIR / "data" / "transcripts"
VECTOR_DIR = PROJECT_DIR / "data" / "vector_db"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
BATCH_SIZE = 5


def split_text(text):
    """Split text into overlapping character chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def main():
    files = []

    for folder in ("podcasts", "newsletters"):
        folder_path = TRANSCRIPT_DIR / folder
        files.extend(folder_path.glob("*.md"))

    if not files:
        print(f"No Markdown files found in {TRANSCRIPT_DIR}")
        return

    client = chromadb.PersistentClient(path=str(VECTOR_DIR))


    if "lenny_sources" in [
          item.name for item in client.list_collections()
    ]:
        client.delete_collection("lenny_sources")

    collection = client.create_collection(
        name="lenny_sources",
        metadata={"hnsw:space": "cosine"}
    )

    documents = []
    ids = []
    metadatas = []

    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        source_type = file_path.parent.name

        for number, chunk in enumerate(split_text(text)):
            chunk_id = hashlib.sha256(
                f"{file_path}|{number}".encode("utf-8")
            ).hexdigest()

            documents.append(chunk)
            ids.append(chunk_id)
            metadatas.append({
                "source": file_path.name,
                "source_type": source_type,
                "chunk": number
            })

    print(f"Prepared {len(documents)} chunks from {len(files)} files.")


    with httpx.Client(timeout=600.0) as http:
        for start in range(0, len(documents), BATCH_SIZE):
            end = min(start + BATCH_SIZE, len(documents))

            # Skip chunks already stored in ChromaDB.
            batch_ids = ids[start:end]
            existing_ids = set(
                collection.get(ids=batch_ids)["ids"]
            )

            missing_indices = [
                i for i in range(start, end)
                if ids[i] not in existing_ids
            ]

            if not missing_indices:
                print(f"Already indexed {end}/{len(documents)} chunks.")
                continue

            batch_documents = [documents[i] for i in missing_indices]
            batch_ids_missing = [ids[i] for i in missing_indices]
            batch_metadatas = [metadatas[i] for i in missing_indices]


            response = http.post(
                 OLLAMA_EMBED_URL,
                 json={
                 "model": EMBED_MODEL,
                 "input": [
                 "search_document: " + document
                 for document in batch_documents
                   ]
                 }
            )
            response.raise_for_status()
            embeddings = response.json()["embeddings"]

            collection.upsert(
                ids=batch_ids_missing,
                documents=batch_documents,
                metadatas=batch_metadatas,
                embeddings=embeddings
            )

            print(
                f"Processed through chunk {end}/{len(documents)} "
                f"(stored: {collection.count()})"
            )

    print(f"Done! Total indexed chunks: {collection.count()}")


if __name__ == "__main__":
    main()
