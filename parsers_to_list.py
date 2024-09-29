import pypdf
import pymupdf
import cv2 as cv
from pdf2image import convert_from_path
import numpy as np
import pytesseract
from PIL import Image
from decorators import time_execution
from llama_parse import LlamaParse
from dotenv import load_dotenv
import os
import shutil

load_dotenv()
llama_cloud_api_key = os.getenv("LLAMA_CLOUD_API_KEY")


@time_execution
def pypdf_parse_to_list(pdf_path: str) -> list[str]:
    page_list = []
    with open(pdf_path, "rb") as f:
        file = pypdf.PdfReader(f,strict=True)
        for page in file.pages:
            text = page.extract_text(space_width=100)
            text = text[0:230000] #limiting the text size
            page_list.append(text)
    return page_list


@time_execution
def pymupdf_parse_to_list(pdf_path: str) -> list[str]:
    page_list = []
    file = pymupdf.open(pdf_path)
    for page_num in range(len(file)):
        page = file.load_page(page_num)
        text = page.get_text()
        text = text[0:230000] #limiting the text size
        page_list.append(text)
    return page_list

@time_execution
def pytesseract_parse_to_list(pdf_path: str, dpi:int=200) -> list[str]:
    page_list = []
    images = convert_from_path(pdf_path, dpi=dpi, fmt='jpeg', poppler_path=shutil.which('pdfinfo'))
    for i, image in enumerate(images):
        image_cv = np.array(image)
        image_cv = cv.cvtColor(image_cv, cv.COLOR_BGR2GRAY)
        image = Image.fromarray(image_cv)
        text = pytesseract.image_to_string(image, lang='heb+eng') 
        text = text[0:230000] #limiting the text size
        page_list.append(text)
    return page_list


@time_execution
def llama_parse_to_list(pdf_path: str) -> str:
    parser = LlamaParse(result_type="markdown",
                        api_key=llama_cloud_api_key,
                        )
    document = parser.load_data(pdf_path)
    return document