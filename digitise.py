import pathlib
import google.generativeai as genai
import PIL.Image
import os
import streamlit as st
from io import BytesIO

# Configure your Google API key
GOOGLE_API_KEY = "API KEY HERE"  # Set your API key here
genai.configure(api_key=GOOGLE_API_KEY)

# Select the model
model = genai.GenerativeModel('models/gemini-2.5-pro-latest')

# Streamlit user interface
st.title("PDF Handwritten Text Extraction")

# File uploader allows multiple PDFs
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

import fitz  # PyMuPDF
import tempfile
from io import BytesIO
import os

def extract_text_from_pdf(uploaded_file):
    # Convert uploaded file to a byte stream
    pdf_file = BytesIO(uploaded_file.read())

    # Create a temporary file to save the PDF content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
        temp_pdf_file.write(pdf_file.getvalue())
        temp_pdf_path = temp_pdf_file.name

    # Open the PDF with PyMuPDF using the temp file path
    pdf_document = fitz.open(temp_pdf_path)

    # Prepare the text content
    extracted_text = ""

    # Iterate over each page in the PDF
    for idx in range(pdf_document.page_count):
        page = pdf_document.load_page(idx)

        # Get the page's image (as pixmap) and save it if necessary
        pix = page.get_pixmap()
        img_path = f"pdf_page_{idx+1}.png"
        pix.save(img_path)

        # Perform OCR or any further processing you need on the image here

        # Add text for this page to the overall extracted text
        extracted_text += f"\nPage {idx+1}:\n{page.get_text()}\n\n"

    # Cleanup: Remove the temporary file
    os.remove(temp_pdf_path)

    return extracted_text



# Handling multiple PDFs
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.write(f"Processing file: {uploaded_file.name}")
        
        # Extract text from the uploaded PDF
        extracted_text = extract_text_from_pdf(uploaded_file)

        # Convert the extracted text to a downloadable file
        txt_filename = os.path.splitext(uploaded_file.name)[0] + '.txt'
        txt_bytes = BytesIO(extracted_text.encode())

        # Display download button for the text file
        st.download_button(
            label=f"Download Extracted Text for {uploaded_file.name}",
            data=txt_bytes,
            file_name=txt_filename,
            mime="text/plain"
        )

else:
    st.info("Please upload one or more PDF files.")
