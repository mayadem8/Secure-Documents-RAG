from flask import Flask, request, jsonify
from flask_cors import CORS
from scripts.search_faiss import search_one


app = Flask(__name__)
# Allow your Vite dev server to call this API
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}})

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json(force=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"error": "Missing 'query'"}), 400

    # --- Run your FAISS search ---
    print(f"\n[Flask] Running FAISS search for query: {query}")
    results = search_one(query)  # <-- This calls your existing code

    # Print results to terminal for debugging
    print("\n[Flask] FAISS Results:")
    for i, (distance, payload) in enumerate(results, start=1):
        print(f"Result {i}:")
        print(f"  Distance: {distance}")
        print(f"  Doc ID: {payload.get('doc_id')}")
        print(f"  Text: {payload.get('text')[:200]}...\n")

    # For now, return a simple confirmation to frontend
    return jsonify({"ok": True, "query": query, "results_count": len(results)})

if __name__ == "__main__":
    # Run on 5000 so it doesn't clash with Vite (5173)
    app.run(host="127.0.0.1", port=5000, debug=True)
