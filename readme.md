# Challenge 1a: PDF Processing Solution ADOBE– README

## 🔍 Overview and Approach

This project provides a solution for extracting the **title** and **heading structure** (outline) from PDF documents. The Python script uses a combination of PDF text extraction and OCR (Optical Character Recognition) to handle both text-based PDFs and scanned-image PDFs.

### Key Steps:

- **Language Detection:**
  - The first page of the PDF is read and scanned for Unicode characters to detect if the content is in English, Hindi, Marathi, or Japanese. This determines which Tesseract OCR language packs to use for any needed OCR processing.
- **Text Extraction (PyMuPDF):**
  - We use the PyMuPDF library to parse the PDF and extract all text spans along with their font sizes. This includes reading each page’s blocks of text and collecting the font sizes of every text span.
- **Heading Detection:**
  - We identify headings by comparing font sizes. The script finds the most common (body) font size, then treats any larger font sizes as potential headings. The largest font sizes on each page are mapped to heading levels (e.g., H1, H2, H3).
- **Title Extraction:**
  - On the first page, the largest text spans are concatenated to form the document title. If no text is found (e.g., a scanned PDF), the first page is converted to an image, and OCR is used to extract the title text.
- **Outline Creation:**
  - As we iterate through each page, any line of text whose font size matches a heading size is added to the outline with its level (H1, H2, H3) and page number.
- **OCR Fallback:**
  - If the PDF has no extractable text (e.g., it’s scanned), we fall back to using pdf2image to convert the page to an image and then run Tesseract OCR via the pytesseract library to recognize text and extract the title.The output is a structured JSON file for each PDF:

---

## 📊 Libraries and Tools

### Python Libraries:

- **PyMuPDF (fitz)**: Extracts structured text with font metadata
- **pytesseract**: Python bindings for Tesseract OCR
- **pdf2image**: Converts PDF pages to images
- **Pillow (PIL)**: Image handling library
- **Other built-ins**: `re`, `os`, `json`, `time`, `collections`

### System Tools:

- **Tesseract OCR** (with language packs): `eng`, `hin`, `mar`, `jpn`
- **Poppler-utils**: Required by `pdf2image` to convert PDF pages

---

## 🚀 Docker Setup

### Dockerfile Summary:

The `Dockerfile` uses `python:3.9-slim` and installs all necessary libraries and dependencies:

- System packages: `poppler-utils`, `tesseract-ocr`, language packs, image libraries, dev tools
- Python dependencies from `requirements.txt`
- Verifies OpenCV installation (though not required for logic)

### Example Dockerfile Excerpt:

```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    tesseract-ocr-jpn \
    tesseract-ocr-mar \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev \
    gcc build-essential pkg-config python3-dev \
    libfreetype6-dev libjpeg-dev zlib1g-dev libopenjp2-7 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
CMD ["python", "process_pdfs.py", "input/"]
```

---

## 🛁 Build and Run Instructions

### Build the Docker Image:

```bash
 docker build --platform linux/amd64 -t hackathon-round1-solver .

### Run the Docker Container:

```bash
docker run --rm -v "${PWD}/input:/app/input:ro" -v "${PWD}/output:/app/output" --network none hackathon-round1-solver

```

- `input/`: Mounts your local input directory containing PDFs.
- `output/`: Outputs JSON files into your local output directory.
- `--network none`: Runs with no network access (per challenge rules).

---

## 📂 Directory Structure

```
project-root/
├── Dockerfile
├── process_pdfs.py
├── requirements.txt
├── input/     # PDF files are placed here
└── output/    # JSON outputs will be saved here
```

### Sample Output Format:

```json
{
  "title": "Extracted Document Title",
  "outline": [
    { "level": "H1", "text": "First Heading", "page": 1 },
    { "level": "H2", "text": "Subheading 1.1", "page": 2 },
    { "level": "H2", "text": "Subheading 1.2", "page": 3 },
    ...
  ]
}
}
```

---

## ✅ Checklist Compliance

This solution satisfies the following challenge criteria:

✅ All PDFs in input/ directory are processed
✅ JSON output files are generated for each PDF
✅ Output format matches the required structure
✅ Output conforms to schema in sample_dataset/schema/output_schema.json
✅ Processing completes within 10 seconds for 50-page PDFs
✅ Solution works without internet access
✅ Memory usage stays within the 16GB limit
✅ Compatible with AMD64 architecture
---

## 🌟 Conclusion

This solution is designed for robust, offline extraction of structured heading outlines and titles from a wide range of PDFs including scanned, multilingual, and poster-style documents. The OCR fallback ensures compatibility across formats, and the Docker setup guarantees reproducibility across environments.

---

For questions, improvements, or further enhancements, feel free to reach out or fork the project!

