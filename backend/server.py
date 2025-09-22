from flask import Flask, request, jsonify
from flask_cors import CORS
from scripts.search_faiss import search_one, rewrite_with_gpt


app = Flask(__name__)
# Allow your Vite dev server to call this API
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}})

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json(force=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"error": "Missing 'query'"}), 400

    # --- Run FAISS search ---
    print(f"\n[Flask] Running FAISS search for query: {query}")
    faiss_results = search_one(query)  # returns top chunks

    # Print FAISS results to terminal
    print("\n[Flask] FAISS Results:")
    for i, (distance, payload) in enumerate(faiss_results, start=1):
        print(f"Result {i}:")
        print(f"  Distance: {distance}")
        print(f"  Doc ID: {payload.get('doc_id')}")
        print(f"  Text: {payload.get('text')[:200]}...\n")

    # --- Generate GPT final answer ---
    print("[Flask] Generating GPT answer...")
    gpt_answer = rewrite_with_gpt(query, faiss_results)

    # Print GPT answer to terminal
    print("\n[Flask] GPT Final Answer:")
    print(gpt_answer)

    # Return both FAISS and GPT to frontend
    return jsonify({
    "ok": True,
    "query": query,
    "results_count": len(faiss_results),
    "gpt_answer": gpt_answer,
    # NEW: send the top doc id (first FAISS hit) back to the UI
    "top_doc_id": (faiss_results[0][1].get("doc_id") if faiss_results else None),
    "results": [
        {
            "distance": float(distance),
            "doc_id": payload.get("doc_id"),
            "text": payload.get("text")[:500]
        }
        for distance, payload in faiss_results
    ]
})

if __name__ == "__main__":
    # Run on 5000 so it doesn't clash with Vite (5173)
    app.run(host="127.0.0.1", port=5000, debug=True)
