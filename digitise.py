import pathlib
import google.generativeai as genai
import PIL.Image
import os
import streamlit as st
from io import BytesIO

# Configure your Google API key
GOOGLE_API_KEY = "AIzaSyDTx5XPB1aSTVmYvOAtjGATWWBtJ3TUGiA"  # Set your API key here
genai.configure(api_key=GOOGLE_API_KEY)

# Select the model
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

# Streamlit user interface
st.title("PDF Handwritten Text Extraction")

# File uploader allows multiple PDFs
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

import fitz  # PyMuPDF

def extract_text_from_pdf(uploaded_file):
    # Convert uploaded file to a byte stream
    pdf_file = BytesIO(uploaded_file.read())

    # Open the PDF with PyMuPDF
    pdf_document = fitz.open(pdf_file)

    # Prepare the text content
    extracted_text = ""

    # Iterate over each page in the PDF
    for idx in range(pdf_document.page_count):
        page = pdf_document.load_page(idx)

        # Get the page's image (as pixmap) and save it if necessary
        pix = page.get_pixmap()
        img_path = f"pdf_page_{idx+1}.png"
        pix.save(img_path)

        # Open the image for OCR
        img = PIL.Image.open(img_path)

        # Perform OCR on the image
        response = model.generate_content(
            [
                f"Task: Extract everything that is asked to be calculated in the question from the attached image. This includes not only the variables but also any intermediate steps, formulas, or values that are necessary to solve the problem. The images contain the handwritten solutions to one or more questions, and you need to extract all the information relevant to each question's solution. The questions are summarized below. Make sure to capture all parts of the solution for each question, including any intermediate steps:\n\n"
                "Q1.For the force shown in Figure 1\n"
                "a) Determine the x, y, and z scalar components of vector F. (Marks 3)\n"
                "b) Express F in Cartesian vector form. (Marks 1)\n"
                "c) Determine the direction angles α, β, and γ of force F with respect to the x, y, and z axes and verify that the direction angles satisfy the requirement cos² α + cos² β + cos² γ = 1 (Marks 3)\n"
                "d) Express F as a product of its magnitude and directional unit vector. (e.g. {10(0.1i + 0.2j + 0.3k)} N). (Marks 1)\n"
                "Q2. Determine the magnitude and direction angles of F3 shown in Figure 2, so that the resultant of the three forces is zero. (Marks 3)\n"
                "Q3: Two cables (AB and AC) act on a hook at point A as shown in Figure 3.\n"
                "a) Determine the position vectors for the internal forces labeled FB and FC. (Marks 2)\n"
                "b) Express forces FB and FC in Cartesian vector form. (Marks 2)\n"
                "c) Determine the resultant force R in Cartesian vector form and then determine its magnitude and direction angles. (Marks 3)\n"
                "d) Determine the angle at A formed by cables AB and AC. (Marks 2)\n"
                f"Image: {img}"
            ],
            stream=True
        )
        response.resolve()

        # Get the extracted text
        if response.candidates:
            if response.candidates[0].content.parts:
                text = response.candidates[0].content.parts[0].text
            else:
                st.warning(f"No generated text found for page {idx+1}.")
                text = "No OCR text found."
        else:
            st.warning(f"No candidates found for page {idx+1}.")
            text = "No OCR text found."

        # Append extracted text to the overall text
        extracted_text += f"\nPage {idx+1}:\n{text}\n\n"

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
