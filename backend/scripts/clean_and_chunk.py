import os
import re
import json
import tiktoken

# --- CONFIG ---
RAW_TEXT_DIR = os.path.join("backend", "output", "raw_txt")

CHUNK_DIR = os.path.join("backend", "output", "chunks")

MAX_TOKENS = 700      # Size of each chunk
OVERLAP_TOKENS = 50   # Overlap between chunks
ENCODING = tiktoken.get_encoding("cl100k_base")  # OpenAI compatible tokenizer

os.makedirs(CHUNK_DIR, exist_ok=True)

def strip_front_matter(text):
    """
    Drop everything before 'Abstract' / 'Introduction' / 'Summary' (case-insensitive),
    since that area usually contains names, emails, affiliations.
    """
    m = re.search(r'\b(abstract|introduction|summary)\b', text, flags=re.IGNORECASE)
    return text[m.start():] if m else text

def clean_text(text):
    """
    Remove sensitive or irrelevant info: emails, URLs, DOIs, phone-like patterns,
    page banners, affiliations/locations keywords, and lightly anonymize names
    in the header area. Also normalize whitespace.
    """

    # 0) Cut author/title/affiliation header if possible
    text = strip_front_matter(text)

    # 1) Emails -> [EMAIL]
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]', text)

    # 2) URLs -> [URL]
    text = re.sub(r'(https?://\S+|www\.\S+)', '[URL]', text, flags=re.IGNORECASE)

    # 3) DOI-like strings -> [DOI]
    text = re.sub(r'\b10\.\d{4,9}/\S+\b', '[DOI]', text)

    # 4) Phone-like patterns -> [PHONE]
    text = re.sub(r'(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4})', '[PHONE]', text)

    # 5) Common org/location keywords -> [ORG]/[LOC]
    text = re.sub(r'\b(University|Institute|Laboratory|Department|Dept\.?|LLC|Inc\.?|Ltd\.?|Company|Corporation|Corp\.?|GmbH|SAS)\b',
                  '[ORG]', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(Tbilisi|Georgia|United States|USA|Germany|France|UK|EU)\b',
                  '[LOC]', text, flags=re.IGNORECASE)

    # 6) Remove '--- PAGE N ---'
    text = re.sub(r'-{2,}\s*PAGE\s*\d+\s*-{2,}', '', text, flags=re.IGNORECASE)

    # 7) Light header-only name redaction (first ~1000 chars)
    header, body = text[:1000], text[1000:]
    # Patterns like "First Last" or "First M. Last" -> [NAME] only in header
    header = re.sub(r'\b[A-Z][a-z]+(?:\s+[A-Z]\.)?(?:\s+[A-Z][a-z]+)\b', '[NAME]', header)

    # 8) Normalize whitespace
    text = (header + body)
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def tokenize_count(text):
    """Count tokens using tiktoken."""
    return len(ENCODING.encode(text))

def chunk_text(text, max_tokens=MAX_TOKENS, overlap=OVERLAP_TOKENS):
    """
    Split text into token-based chunks with token overlap.
    """
    token_ids = ENCODING.encode(text)
    chunks = []
    start = 0
    n = len(token_ids)

    while start < n:
        end = min(start + max_tokens, n)
        window = token_ids[start:end]
        chunk = ENCODING.decode(window)
        chunks.append(chunk)
        if end == n:
            break
        # advance with overlap
        start = end - overlap if end - overlap > start else end

    return chunks

def process_file(input_path, output_path, doc_id):
    """Clean, chunk, and save as JSON."""
    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    clean = clean_text(raw_text)
    chunks = chunk_text(clean)

    output_data = []
    for idx, chunk in enumerate(chunks):
        output_data.append({
            "doc_id": doc_id,
            "chunk_id": idx,
            "text": chunk,
            "token_count": tokenize_count(chunk)
        })

    # Save JSON
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(output_data, out, ensure_ascii=False, indent=2)

def process_all_files():
    for root, _, files in os.walk(RAW_TEXT_DIR):
        for file in files:
            if file.lower().endswith(".txt"):
                input_path = os.path.join(root, file)
                output_file = file.replace(".txt", "_chunks.json")
                output_path = os.path.join(CHUNK_DIR, output_file)

                print(f"Processing {file} ...")
                doc_id = os.path.splitext(file)[0]

                process_file(input_path, output_path, doc_id)
                print(f"Saved chunks to {output_path}")

if __name__ == "__main__":
    process_all_files()
    print("✅ All files cleaned and chunked!")
