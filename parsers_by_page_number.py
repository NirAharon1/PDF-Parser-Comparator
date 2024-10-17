"""
This module provides functions for parsing PDF files and extracting text from specific pages using various libraries.
The functions in this module allow users to extract text from PDF pages using different parsing methods.
Each function is designed to handle a specific parsing library and return the extracted text for a given page number.
"""

import io
import pypdf
import pymupdf
from pdf2image import convert_from_path
import pytesseract
import pymupdf4llm
import aspose.words as aw
from decorators import time_execution


@time_execution
def pypdf_parse_page(pdf_path: str, page_number: int) -> str:
    with open(pdf_path, "rb") as f:
        reader = pypdf.PdfReader(f, strict=True)
        page = reader.pages[page_number]
        text = page.extract_text(space_width=100)[:230000]  # limiting the text size
    return text


@time_execution
def pymupdf_parse_page(pdf_path: str, page_number: int) -> str:
    with pymupdf.open(pdf_path) as file:
        page = file.load_page(page_number)
        text = page.get_text()[:230000]  # limiting the text size
    return text

@time_execution
def pymupdf4llm_parse_page(pdf_path: str, page_number: int) -> str:
    return pymupdf4llm.to_markdown(pdf_path, write_images=False, pages=[page_number])



@time_execution
def pytesseract_parse_page(pdf_path: str, page_number: int) -> str:
    if images := convert_from_path(pdf_path, dpi=300, first_page=page_number, last_page=page_number):
        image = images[0].convert('L')  # Convert directly to grayscale
        text = pytesseract.image_to_string(image, lang='heb+eng')[:230000]  # limiting the text size
    return text


@time_execution
def aspose_parse_page(pdf_path: str, page_number: int) -> str:
    load_options = aw.loading.PdfLoadOptions()
    load_options.page_index = page_number
    load_options.page_count = 1
    doc = aw.Document(pdf_path, load_options)
    save_options = aw.saving.MarkdownSaveOptions() 
    save_options.images_folder = "aspose_temp_images"

    with io.BytesIO() as stream:
        doc.save(stream, save_options)
        stream.seek(0)# Convert the stream to a string
        return stream.read().decode('utf-8')
