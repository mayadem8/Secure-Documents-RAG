import os
import numpy as np
import faiss
import json

# Paths
EMBED_DIR = os.path.join("backend", "output", "embeddings")
INDEX_DIR = os.path.join("backend", "output", "faiss_index")

os.makedirs(INDEX_DIR, exist_ok=True)

INDEX_FILE = os.path.join(INDEX_DIR, "company_docs.index")
METADATA_FILE = os.path.join(INDEX_DIR, "metadata.json")

VECTOR_SIZE = 384  # For MiniLM-L12-v2

def build_index():
    vectors = []
    metadata = []

    print("Loading embeddings...")

    for file in os.listdir(EMBED_DIR):
        if file.endswith(".npz"):
            path = os.path.join(EMBED_DIR, file)
            data = np.load(path, allow_pickle=True)

            embeddings = data["embeddings"]
            metas = data["metadata"]

            vectors.append(embeddings)
            metadata.extend(metas)

    if not vectors:
        raise ValueError("No embeddings found! Run generate_embeddings.py first.")

    # Combine all embeddings into one numpy array
    vectors = np.vstack(vectors).astype('float32')

    print(f"Total vectors loaded: {vectors.shape[0]}")

    # Create FAISS index
    index = faiss.IndexFlatL2(VECTOR_SIZE)
    index.add(vectors)

    # Save the index
    faiss.write_index(index, INDEX_FILE)
    print(f"FAISS index saved to {INDEX_FILE}")

    # Save metadata
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Metadata saved to {METADATA_FILE}")

if __name__ == "__main__":
    build_index()
