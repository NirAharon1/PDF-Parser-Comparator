import pypdf
import pymupdf
from decorators import time_execution
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import numpy as np
import cv2 as cv
import pymupdf4llm
import aspose.words as aw
import io



@time_execution
def pypdf_parse_page(pdf_path: str, page_number: int) -> str:
    with open(pdf_path, "rb") as f:
        text = ""
        reader = pypdf.PdfReader(f,strict=True)
        page = reader.pages[page_number]
        text += page.extract_text(space_width=100)
        text = text[0:230000] #limiting the text size
    return text


@time_execution
def pymupdf_parse_page(pdf_path: str, page_number: int) -> str:
    text = ""
    file = pymupdf.open(pdf_path)
    page = file.load_page(page_number)
    text += page.get_text()
    text = text[0:230000] #limiting the text size
    return text


@time_execution
def pymupdf4llm_parse_page(pdf_path: str, page_number: int) -> str:
    text = pymupdf4llm.to_markdown(pdf_path, 
                                   write_images=False,
                                   pages=[page_number],
                                   )
    return text


@time_execution
def pytesseract_parse_page(pdf_path: str, page_number: int) -> str:
    text = ''
    images = convert_from_path(pdf_path, dpi=300, first_page=page_number, last_page=page_number)
    if images:
        image = images[0]
        image_cv = np.array(image)  
        image_cv = cv.cvtColor(image_cv, cv.COLOR_BGR2GRAY)
        image = Image.fromarray(image_cv)
        text = pytesseract.image_to_string(image, lang='heb+eng') 
        text = text[0:230000] #limiting the text size
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
        text = stream.read().decode('utf-8')
        return text
    

