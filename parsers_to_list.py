import os
import shutil
import pypdf
import pymupdf
from pdf2image import convert_from_path
import pytesseract
from llama_parse import LlamaParse
from dotenv import load_dotenv
from decorators import time_execution
import pdfplumber

load_dotenv()
llama_cloud_api_key = os.getenv("LLAMA_CLOUD_API_KEY")


@time_execution
def pypdf_parse_to_list(pdf_path: str) -> list[str]:
    with open(pdf_path, "rb") as f:
        file = pypdf.PdfReader(f, strict=True)
        return [page.extract_text(space_width=100)[:230000] for page in file.pages]

@time_execution
def pymupdf_parse_to_list(pdf_path: str) -> list[str]:
    with pymupdf.open(pdf_path) as file:
        return [file.load_page(page_num).get_text()[:230000] for page_num in range(len(file))]
    

@time_execution
def pytesseract_parse_to_list(pdf_path: str, dpi:int=200) -> list[str]:
    images = convert_from_path(pdf_path, dpi=dpi, fmt='jpeg', poppler_path=shutil.which('pdfinfo'))
    return [pytesseract.image_to_string(image.convert('L'), lang='heb+eng')[:230000] for image in images]


@time_execution
def llama_parse_to_list(pdf_path: str) -> str:
    parser = LlamaParse(result_type="markdown", api_key=llama_cloud_api_key)
    return parser.load_data(pdf_path)


@time_execution
def pdfplumber_parse_to_list(pdf_path: str) -> list[str]:
    with pdfplumber.open(pdf_path) as pdf:
        return [page.extract_text()[:230000] if page.extract_text() else "" for page in pdf.pages]