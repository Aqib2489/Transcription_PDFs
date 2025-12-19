# PDF Text Extraction Tool

A simple Streamlit web app for extracting text from PDF files using PyMuPDF. Upload one or more PDFs and download the extracted text as `.txt` files.

---

## What It Does

- Upload multiple PDF files
- Extract text from each page
- Download extracted text as `.txt` files

---

## Requirements

```
streamlit
google-generativeai
pymupdf
Pillow
numpy
opencv-python-headless
PyPDF2
```

---

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure API Key (if needed):**
   - Edit `digitise.py` line 9
   - Replace `"API KEY HERE"` with your Google API key

3. **Run the app:**
```bash
streamlit run digitise.py
```

The app opens in your browser at `http://localhost:8501`

---

## Usage

1. Click "Browse files" to upload PDF(s)
2. Wait for processing
3. Click "Download Extracted Text" for each file
4. Text saved as `filename.txt`

---

## How It Works

1. **Upload:** File converted to byte stream
2. **Extract:** PyMuPDF reads PDF pages and extracts text
3. **Download:** Text saved as `.txt` file

**Code flow:**
```python
def extract_text_from_pdf(uploaded_file):
    # Convert to temporary file
    pdf_document = fitz.open(temp_pdf_path)
    
    # Extract text from each page
    for idx in range(pdf_document.page_count):
        page = pdf_document.load_page(idx)
        extracted_text += page.get_text()
    
    return extracted_text
```

---

## Author

**Mohammad Aqib**  
Email: maqib@ualberta.ca  
University of Alberta

---

## License

Open-source for educational use.
