import fitz  
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import os
import json
import time
from collections import Counter

def detect_language(sample_text):
    if re.search(r'[\u0900-\u097F]', sample_text):
        return 'hin+mar'
    if re.search(r'[\u3040-\u30FF\u4E00-\u9FFF]', sample_text):
        return 'jpn'
    return 'eng'

def extract_headings(pdf_path):
    doc = fitz.open(pdf_path)
    n_pages = doc.page_count

    sample_text = ""
    for i in range(min(2, n_pages)):
        sample_text += doc.load_page(i).get_text()

    language = detect_language(sample_text)

    all_sizes = []
    for i in range(n_pages):
        page = doc.load_page(i)
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                for span in line["spans"]:
                    all_sizes.append(span['size'])

    if not all_sizes:
        first_image = convert_from_path(pdf_path, first_page=1, last_page=1)[0]
        ocr_text = pytesseract.image_to_string(first_image, lang=language)
        sample_text = ocr_text
        language = detect_language(sample_text)
        most_common_size = 0
        heading_sizes = []
    else:
        size_counts = Counter(all_sizes)
        most_common_size, _ = size_counts.most_common(1)[0]
        heading_sizes = sorted({s for s in all_sizes if s > most_common_size}, reverse=True)

    size_to_level = {}
    if len(heading_sizes) > 0:
        size_to_level[heading_sizes[0]] = "H1"
    if len(heading_sizes) > 1:
        size_to_level[heading_sizes[1]] = "H2"
    if len(heading_sizes) > 2:
        size_to_level[heading_sizes[2]] = "H3"

    title_text = ""
    outline = []

    for i in range(n_pages):
        page = doc.load_page(i)
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                line_text = "".join(span['text'] for span in line["spans"]).strip()
                if not line_text:
                    continue

                if i == 0:
                    span_sizes = [span['size'] for span in line["spans"]]
                    max_size = max(span_sizes) if span_sizes else 0
                    try:
                        biggest_size = max(
                            s['size']
                            for blk in blocks
                            if "lines" in blk
                            for ln in blk["lines"]
                            for s in ln["spans"]
                        )
                    except:
                        biggest_size = 0
                    if max_size and max_size == biggest_size:
                        title_text += (line_text + " ")

                span_sizes = [span['size'] for span in line["spans"]]
                max_span = max(span_sizes) if span_sizes else 0
                if max_span in size_to_level:
                    # Detect visible page number
                    visible_page_number = None
                    for line_check in blocks:
                        if "lines" not in line_check:
                            continue
                        for l in line_check["lines"]:
                            line_text_check = "".join(span['text'] for span in l["spans"]).strip()
                            if re.fullmatch(r"\d{1,4}", line_text_check):
                                visible_page_number = int(line_text_check)
                                break
                        if visible_page_number is not None:
                            break

                    page_number = visible_page_number if visible_page_number is not None else i
                    outline.append({
                        "level": size_to_level[max_span],
                        "text": line_text,
                        "page": page_number
                    })

        if i == 0 and not title_text:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr = pytesseract.image_to_string(img, lang=language)
            for line in ocr.splitlines():
                if line.strip():
                    title_text = line.strip()
                    break

    if not title_text and n_pages > 0:
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ocr = pytesseract.image_to_string(img, lang=language)
        title_text = ocr.splitlines()[0].strip()

    return {
        "title": title_text.strip(),
        "outline": outline
    }

if __name__ == "__main__":
    input_dir = "input"
    output_dir = "output"

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        exit(1)

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("❗ No PDF files found in input/")
        exit(1)

    existing_jsons = [f for f in os.listdir(output_dir) if f.lower().endswith(".json")]
    valid_jsons = {f.replace(".pdf", ".json") for f in pdf_files}
    for json_file in existing_jsons:
        if json_file not in valid_jsons:
            try:
                os.remove(os.path.join(output_dir, json_file))
            except:
                pass  

    for filename in pdf_files:
        pdf_path = os.path.join(input_dir, filename)
        json_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))

        print(f"\n📄 Processing: {filename}")
        start = time.time()
        try:
            result = extract_headings(pdf_path)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            end = time.time()
            print(f"✅ Done in {end - start:.2f} sec → {json_path}")
        except Exception as e:
            print(f"❌ Error processing {filename}: {type(e).__name__} - {e}")
