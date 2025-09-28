import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import re
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY missing in .env")
client = OpenAI(api_key=OPENAI_API_KEY)

# Paths
INDEX_FILE = "backend/output/faiss_index/company_docs.index"
METADATA_FILE = "backend/output/faiss_index/metadata.json"

# Load the same embedding model used for indexing
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

# Load FAISS index + metadata
index = faiss.read_index(INDEX_FILE)
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Heuristics to down-rank/remove mathy chunks
MATH_CHARS = set("=+−–—*/^_()[]{}<>∫∑√≈≃≅≡≤≥∞∇·×÷°′″βγδΔλμπσφΩωΨψαηθκνξρτχζ…")
def is_math_heavy(s: str, threshold: float = 0.15) -> bool:
    if not s:
        return False
    nonalnum = sum(1 for c in s if not c.isalnum() and c not in " .,:;-'\"")
    mathsym = sum(1 for c in s if c in MATH_CHARS)
    ratio = (nonalnum + mathsym) / max(1, len(s))
    # also zap LaTeX-ish bits quickly
    if re.search(r'\\[a-zA-Z]+|[\$\^_]{1}', s):
        ratio = max(ratio, 0.2)
    return ratio > threshold


def search_one(query: str):
    # 1) Encode query
    q = model.encode([query]).astype("float32")

    # 2) Search FAISS index
    distances, indices = index.search(q, 20)

    candidates = []
    for d, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue

        p = metadata[idx]
        text = p.get("text", "")

        # REMOVE MATH FILTERING COMPLETELY
        # No skipping or penalties for math chunks now

        # Convert FAISS distance to similarity
        sim = 1.0 / (1.0 + float(d))
        final = sim

        candidates.append((final, d, p))

    if not candidates:
        best_idx = indices[0][0]
        return distances[0][0], metadata[best_idx]

    # Sort by similarity
    candidates.sort(reverse=True, key=lambda x: x[0])

    top_chunks = [(d, p) for _, d, p in candidates]
    all_doc_ids = list({p.get("doc_id") for _, p in top_chunks if p.get("doc_id")})

    return top_chunks, all_doc_ids


 




def rewrite_with_gpt(question: str, chunks: list) -> str:
    """
    Takes the top FAISS chunks and rewrites them into a concise, user-friendly answer.
    """
    # Combine multiple chunks into one context
    combined_context = "\n\n".join([c[1].get("text", "") for c in chunks])

    prompt = f"""
You are given multiple text excerpts from technical documents and a user question.
Write a report to the question using ONLY the information in these texts.

Instructions:
- Do NOT add any new facts that aren't explicitly in the texts.
- Write as technically and specifically as possible.
- rerurn math and technicall examples if possible
- Write general descriptions and words as less as possible.
- If there are numerical values, include them accurately.
- report should be as detailed as possible, as long as possible while still being relevant.
- If the texts don't contain the answer, say "The provided documents do not contain sufficient information. 
- Dont return references



Question: {question}

Text Excerpts:
{combined_context}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # fast and cost-efficient
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    query = "What percentage of defective area can modern magnetic flaw detectors identify in steel wire ropes?"

    # Get top 3 FAISS chunks
    top_results = search_one(query)

    print("\nTop 3 Semantic Search Results:")
    for i, (d, p) in enumerate(top_results, start=1):
        print(f"\nResult {i}:")
        print(f"Distance: {d:.4f}")
        print(f"Doc ID: {p.get('doc_id', 'N/A')}")
        print(f"Text: {p.get('text', '')[:500]}...")  # preview first 500 chars

    # Send all 3 chunks to GPT for rewriting
    print("\n--- GPT Rewritten Answer ---")
    final_answer = rewrite_with_gpt(query, top_results)
    print(final_answer)

