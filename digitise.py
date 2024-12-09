import os
import zipfile
import tempfile
import fitz
import streamlit as st

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

def save_txt_files_from_pdf(pdf_file, images, output_folder):
    # Extract text from the images
    # Note: Here you can integrate the Gemini or OCR process to extract text
    txt_filename = os.path.splitext(pdf_file.name)[0] + '.txt'
    output_text_file = os.path.join(output_folder, txt_filename)

    with open(output_text_file, 'w') as f:
        # For each image, extract the text (Here, use OCR or generative model logic)
        for idx, img in enumerate(images):
            # Dummy extracted text - replace with actual extraction logic
            text = f"Extracted text for page {idx + 1} of {pdf_file.name}\n"
            f.write(text)
        
        # Delete temporary images
        print(f"Cleaning up temporary images for {pdf_file.name}")
    
    return output_text_file

# Streamlit UI
st.title("PDF Text Extraction and Zipping")

uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_filename = os.path.join(tmpdirname, "extracted_texts.zip")
        
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for pdf_file in uploaded_files:
                pdf_path = os.path.join(tmpdirname, pdf_file.name)
                
                # Save the uploaded PDF file to the temp directory
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_file.getbuffer())
                
                # Extract images from PDF using PyMuPDF
                images = pdf_to_images(pdf_path)
                
                # Save the extracted text in the txt file
                txt_file_path = save_txt_files_from_pdf(pdf_file, images, tmpdirname)
                
                # Add the txt file to the zip archive
                zipf.write(txt_file_path, os.path.basename(txt_file_path))
        
        # Allow the user to download the zip file
        with open(zip_filename, "rb") as f:
            st.download_button("Download Zip File", f, file_name="extracted_texts.zip")
