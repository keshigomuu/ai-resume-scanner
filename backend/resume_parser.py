from typing import Union
import PyPDF2

def extract_text_from_pdf(pdf_path: Union[str, bytes]) -> str:
    """
    Reads a PDF from a file path or bytes and returns its full text.
    """
    text = ""
    # If pdf_path is bytes, wrap in a BytesIO
    if isinstance(pdf_path, bytes):
        from io import BytesIO
        pdf_stream = BytesIO(pdf_path)
        reader = PyPDF2.PdfReader(pdf_stream)
    else:
        reader = PyPDF2.PdfReader(pdf_path)

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text() or ""
        text += "\n"
    return text
