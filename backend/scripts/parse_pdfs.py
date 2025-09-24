import os
from pypdf import PdfReader

# --- CONFIG ---
PDF_ROOT = os.path.join("backend", "data")
OUTPUT_ROOT = os.path.join("backend", "output", "raw_txt")

os.makedirs(OUTPUT_ROOT, exist_ok=True)

def parse_pdf(file_path):
    """Extract text from each page of a single PDF."""
    reader = PdfReader(file_path)
    pages_data = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages_data.append({
            "page": page_num,
            "text": text.strip()
        })
    return pages_data

def process_all_pdfs():
    """Walk through all subfolders, parse PDFs, save text."""
    for root, _, files in os.walk(PDF_ROOT):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, filename)

                # Derive relative folder path (e.g., "2000")
                relative_path = os.path.relpath(root, PDF_ROOT)

                # Create matching output folder
                output_dir = os.path.join(OUTPUT_ROOT, relative_path)
                os.makedirs(output_dir, exist_ok=True)

                # Output file will have same name but .txt
                output_filename = os.path.splitext(filename)[0] + ".txt"
                output_path = os.path.join(output_dir, output_filename)

                print(f"Parsing: {relative_path}/{filename}...")

                # Parse PDF
                pages = parse_pdf(pdf_path)

                with open(output_path, "w", encoding="utf-8") as f:
                    for page in pages:
                        f.write(f"\n--- PAGE {page['page']} ---\n")
                        f.write(page["text"])
                        f.write("\n\n")

                print(f"Saved text to: {output_path}")

if __name__ == "__main__":
    process_all_pdfs()
    print("Done! All PDFs parsed and saved as text.")
