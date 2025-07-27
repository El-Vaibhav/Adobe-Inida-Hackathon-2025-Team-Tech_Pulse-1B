import fitz  # PyMuPDF 📄

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from each page of the given PDF. 🔍

    This function reads a PDF file and extracts text from each page,
    returning a list of dictionaries with page numbers and text content.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        list: A list of dictionaries, each containing:
            - page_number (int): The page number, starting from 1.
            - text (str): The full text content of the page.
    """
    # Open the PDF document 📖
    doc = fitz.open(pdf_path)
    extracted = []

    # Iterate through each page in the document 🔄
    for page_number in range(len(doc)):
        # Load the current page 📄
        page = doc.load_page(page_number)
        # Extract text from the page 📝
        text = page.get_text()

        # Skip empty pages to save space and processing time ⏭️
        if text.strip():
            extracted.append({
                "page_number": page_number + 1,  # Page numbers start from 1 for readability
                "text": text  # Full text content of the page
            })

    # Close the document to free resources 🗑️
    doc.close()

    # Return the extracted text from all pages 🔙
    return extracted
