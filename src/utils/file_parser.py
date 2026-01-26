"""
File Parser Utility

Handles extraction of text from uploaded resume files (PDF, DOCX).
"""

import io
from typing import Union
import pypdf
import docx

def extract_resume_text(file_obj, filename: str) -> str:
    """
    Extract text from an uploaded resume file.
    
    Args:
        file_obj: Streamlit UploadedFile or bytes
        filename: Name of the file with extension
        
    Returns:
        str: Extracted text content
        
    Raises:
        ValueError: If file format is not supported or extraction fails
    """
    file_ext = filename.lower().split('.')[-1]
    text = ""
    
    try:
        if file_ext == 'pdf':
            pdf_reader = pypdf.PdfReader(file_obj)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
        elif file_ext in ['docx', 'doc']:
            # python-docx expects a file-like object
            doc = docx.Document(file_obj)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
                
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Please upload PDF or DOCX.")
            
        return text.strip()
        
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")
