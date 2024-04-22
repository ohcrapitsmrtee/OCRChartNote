import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract
import tempfile
import os
import subprocess

# Add directories to the PATH environment variable
os.environ['PATH'] += os.pathsep + '/usr/bin' + os.pathsep + '/usr/local/bin'

def check_pdfinfo():
    try:
        # Look for 'pdfinfo' in the PATH and common locations
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        common_dirs = ['/usr/bin', '/usr/local/bin', '/bin', '/opt/bin', '/usr/local/share/bin']
        all_dirs = set(path_dirs + common_dirs)
        
        found_paths = [os.path.join(dir, 'pdfinfo') for dir in all_dirs if os.path.isfile(os.path.join(dir, 'pdfinfo'))]
        if found_paths:
            result = subprocess.run(found_paths[0], capture_output=True, text=True)
            return f"pdfinfo is installed at {found_paths[0]}. Output:\n{result.stdout}"
        else:
            return "pdfinfo executable not found in any checked paths."
    except Exception as e:
        return f"An error occurred: {str(e)}"

st.write(check_pdfinfo())

def perform_ocr(uploaded_file, redact_words):
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    # Convert PDF to images
    pages = convert_from_bytes(open(temp_file_path, "rb").read())

    # Perform OCR
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)

    # Redact specified words
    for word in redact_words:
        text = text.replace(word, "*" * len(word))

    # Delete temporary file
    os.unlink(temp_file_path)

    return text, pages

def main():
    st.title("PDF Redaction & OCR Tool")

    # File upload
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    # Redact words prompt
    redact_words = st.text_input("Enter words to redact (comma-separated)", "patient name,confidential")

    if uploaded_file is not None:
        # Perform OCR and redaction
        text, pages = perform_ocr(uploaded_file, [word.strip() for word in redact_words.split(',')])

        # Display redacted OCR result
        st.header("Redacted OCR Result")
        st.text_area("Redacted Text", text, height=400)

        # Display images
        for i, page in enumerate(pages):
            st.image(page, caption=f"Page {i+1}", use_column_width=True)

        # Save redacted text to file
        if st.button("Save Redacted Text"):
            with open("redacted_text.txt", "w") as file:
                file.write(text)
            st.success("Redacted text saved successfully as redacted_text.txt")

if __name__ == "__main__":
    main()
