import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np

# --- CONFIG ---
CHUNK_DIR = os.path.join("backend", "output", "chunks")
EMBED_DIR = os.path.join("backend", "output", "embeddings")

os.makedirs(EMBED_DIR, exist_ok=True)

# Load embedding model
print("Loading embedding")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")


def embed_chunks(input_path, output_path):
    """Load chunk JSON, generate embeddings, save as .npz"""
    with open(input_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [chunk["text"] for chunk in chunks]
    print(f"Generating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    # Save as compressed numpy file with metadata
    np.savez_compressed(output_path,
                        embeddings=embeddings,
                        metadata=chunks)
    print(f"Saved embeddings to {output_path}")

def process_all_chunks():
    for file in os.listdir(CHUNK_DIR):
        if file.endswith("_chunks.json"):
            input_path = os.path.join(CHUNK_DIR, file)
            output_file = file.replace("_chunks.json", "_embeddings.npz")
            output_path = os.path.join(EMBED_DIR, output_file)

            print(f"\nProcessing {file} ...")
            embed_chunks(input_path, output_path)

if __name__ == "__main__":
    process_all_chunks()
    print("✅ All chunks converted to embeddings!")
