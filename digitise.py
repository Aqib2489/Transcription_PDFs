import os
import zipfile
import fitz  # PyMuPDF for PDF to image conversion
import google.generativeai as genai
from PIL import Image
import streamlit as st
import tempfile
import shutil

import fitz  # PyMuPDF
import io

def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    
    # Iterate through each page and convert it to an image
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Load the page
        pix = page.get_pixmap()  # Render the page to an image
        
        # Convert the image to PNG bytes
        img_bytes = pix.tobytes("png")
        images.append(img_bytes)
    
    return images



# Function to convert PDF to images (using PyMuPDF)
def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Get the page
        pix = page.get_pixmap()  # Render page to image
        img_bytes = pix.tobytes("png")  # Convert to PNG bytes
        images.append(img_bytes)
    return images





# Function to extract text using Gemini
def extract_text_from_pdf(pdf_file, api_key, question):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    # Convert PDF to images
    images = pdf_to_images(pdf_file)

    extracted_text = []

    # Temporary folder to store images
    temp_dir = tempfile.mkdtemp()

    # Iterate over extracted images and perform OCR
    for idx, img_bytes in enumerate(images):
        img_path = os.path.join(temp_dir, f'pdf_page_{idx + 1}.png')

        # Save the image
        with open(img_path, 'wb') as img_file:
            img_file.write(img_bytes)

        # Open the image for OCR
        img = Image.open(img_path)

        # Prepare prompt with the user’s question
        prompt = f"""
        Task: Extract everything that is asked to be calculated in the question from the attached image. This includes not only the variables but also any intermediate steps, formulas, or values that are necessary to solve the problem. The images contain the handwritten solutions to one or more questions, and you need to extract all the information relevant to each question's solution. The questions are summarized below. Make sure to capture all parts of the solution for each question, including any intermediate steps:

        {question}
        Image:
        {img}
        """

        # Perform OCR on the image by passing it to the generative model
        response = model.generate_content([prompt], stream=True)
        response.resolve()

        if response.candidates and response.candidates[0].content.parts:
            text = response.candidates[0].content.parts[0].text
        else:
            text = "No text extracted from image."

        extracted_text.append(f"Page {idx + 1}:\n{text}\n")

    # Clean up temporary images after processing
    shutil.rmtree(temp_dir)

    return extracted_text

# Function to save each PDF’s extracted text in its own text file and create a zip of all txt files
def save_extracted_text_to_zip(extracted_text, pdf_filename):
    # Create a zip buffer to store the extracted text files
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Save extracted text for each PDF in a separate text file
        zip_file.writestr(f'{pdf_filename}.txt', '\n'.join(extracted_text))
    zip_buffer.seek(0)
    return zip_buffer

# Streamlit UI
st.title("PDF Text Extraction with Gemini")

# User input for API key
api_key = st.text_input("Enter your Google API key:")

# User input for custom question
question = st.text_area("Enter the question to merge with the prompt:")

# File uploader for multiple PDF files
pdf_files = st.file_uploader("Upload your PDF files", type="pdf", accept_multiple_files=True)

if pdf_files and api_key and question:
    zip_buffer = io.BytesIO()  # This will store the zip file with all the text files
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for pdf_file in pdf_files:
            # Use an in-memory BytesIO buffer for the uploaded PDF
            pdf_data = pdf_file.read()

            # Save the uploaded PDF data to a temporary file in memory
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
                temp_pdf_file.write(pdf_data)
                temp_pdf_path = temp_pdf_file.name
            
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(temp_pdf_path, api_key, question)

            # Create a zip file for the extracted text from the current PDF
            zip_file.writestr(f'{os.path.splitext(pdf_file.name)[0]}.txt', '\n'.join(extracted_text))
            
            # Clean up the temporary PDF file
            os.remove(temp_pdf_path)

    # Provide the zip file for download
    zip_buffer.seek(0)  # Go to the beginning of the zip buffer
    st.download_button(
        label="Download Extracted Text as ZIP",
        data=zip_buffer,
        file_name="extracted_text_files.zip",
        mime="application/zip"
    )
    
    # Optionally, show some extracted text preview
    st.subheader("Preview of Extracted Text:")
    st.text("\n".join(extracted_text[:3]))  # Show first 3 pages as a preview
