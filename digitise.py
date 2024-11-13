import streamlit as st
import pathlib
import google.generativeai as genai
from pdf2image import convert_from_path  # To extract images from PDF
import PIL.Image
import zipfile
import io
import os

# Streamlit UI
st.title("Tool for digitising student's Assignment")

# Input for the Google API key
GOOGLE_API_KEY = st.text_input("Enter your Google API Key:", type="password")

# Validate if API Key is entered
if GOOGLE_API_KEY:
    # Configure the API key
    genai.configure(api_key=GOOGLE_API_KEY)

    # Select the model
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    # Function to process the PDF and extract information based on the question
    def process_pdf(pdf_file, question):
        # Convert PDF to images
        images = convert_from_path(pdf_file)

        # Prepare the output text
        output_text = ""

        # Iterate over extracted images and perform OCR
        for idx, img in enumerate(images):
            # Perform OCR on the image by passing it to the generative model
            response = model.generate_content(
                [
                    f"Task: Extract everything that is asked to be calculated in the question from the attached image. This includes not only the variables but also any intermediate steps, formulas, or values that are necessary to solve the problem. The images contain the handwritten solutions to one or more questions, and you need to extract all the information relevant to each question's solution. The questions are summarized below. Make sure to capture all parts of the solution for each question, including any intermediate steps:"

                    f"Question: {question}"  # Include the user inputted question here

                    f"Image:", img
                ],
                stream=True
            )
            response.resolve()

            # Get the extracted text
            text = response.text

            # Append extracted text to the output text
            output_text += f"\nPage {idx + 1}:\n{text}\n\n"

        return output_text

    # File uploader for multiple PDFs
    pdf_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    # Input for the question
    question = st.text_area("Enter all the question of assignments:")

    # Button to start processing
    if st.button("Process PDFs"):
        if pdf_files and question.strip():
            # Display a progress message
            st.write("Processing... Please wait.")
            
            # Create a progress bar
            progress_bar = st.progress(0)
            
            # Create a buffer to hold the zip file
            zip_buffer = io.BytesIO()

            # Create a ZipFile in memory
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Process each uploaded PDF
                for idx, pdf_file in enumerate(pdf_files):
                    # Create a temporary path for the uploaded PDF file
                    pdf_path = pathlib.Path("/tmp") / pdf_file.name

                    # Save the uploaded PDF to the temporary path
                    with open(pdf_path, "wb") as f:
                        f.write(pdf_file.getbuffer())

                    # Process the PDF and get the extracted text
                    extracted_text = process_pdf(pdf_path, question)

                    # Prepare the name of the .txt file
                    txt_filename = pdf_file.name.replace('.pdf', '.txt')

                    # Write the extracted text to the zip archive
                    zip_file.writestr(txt_filename, extracted_text)

                    # Update the progress bar
                    progress = (idx + 1) / len(pdf_files)
                    progress_bar.progress(progress)

                    st.write(f"Extracted text from {pdf_file.name} has been added to the zip archive.")

            # Seek to the beginning of the zip buffer
            zip_buffer.seek(0)

            # Provide the download button for the zip file
            st.download_button(
                label="Download all text files as ZIP",
                data=zip_buffer,
                file_name="digitised_pdfs.zip",
                mime="application/zip"
            )

            st.success("All PDFs processed and text added to ZIP file.")
        else:
            st.error("Please upload at least one PDF and enter a valid question.")

else:
    st.warning("Please enter your Google API key to start.")

