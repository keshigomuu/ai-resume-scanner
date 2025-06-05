from typing import Union
import os
from resume_parser import extract_text_from_pdf

def extract_text_from_jd(jd_file: Union[str, bytes], filename: str = None) -> str:
    """
    If jd_file is bytes or path pointing to a PDF, extract PDF text.
    Otherwise, treat as plain text and return directly.
    Pass 'filename' (e.g., 'job_desc.pdf' or 'jd.txt') to infer type.
    """
    # If we detect a PDF extension in the filename, call PDF extractor:
    if filename and filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(jd_file)
    # Otherwise, assume jd_file is either a string path to .txt or raw text bytes:
    if isinstance(jd_file, bytes):
        # decode assuming UTF-8
        return jd_file.decode("utf-8", errors="ignore")
    elif isinstance(jd_file, str) and os.path.isfile(jd_file):
        # It's a path to a .txt file
        with open(jd_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # jd_file is already a text string
        return str(jd_file)
