"""
Streamlit app for a comparative analysis tool for PDF parsing libraries.
Allows users to test different parsers on their own PDFs and view performance metrics in real-time
"""

import os
from dataclasses import dataclass, field

from pypdf import PdfReader
import streamlit as st
import pypdfium2 as pdfium
import parsers_to_list

import parsers_by_page_number


st.set_page_config(page_title='PDF parsers compering', layout="wide")
st.title("PDF parsers compering")

PDF_FOLDER_PATH = "PDF_folder"
USER_PDF_FOLDER_PATH = "user_pdf"
box_labels = ["pypdf", "pymupdf", "pymupdf4llm", "pytesseract", "aspose", "llama_parser"]

if 'initialized' not in st.session_state:
    st.session_state.pdf_names = []
    st.session_state.pdf = {}
    st.session_state['initialized'] = True

    try:
        PDF_folder = os.listdir(PDF_FOLDER_PATH)
        for file_name in PDF_folder:
            # Check if the file is a PDF
            if file_name.endswith('.pdf'):
                st.session_state.pdf_names.append(os.path.splitext(file_name)[0])
                st.session_state.pdf[os.path.splitext(file_name)[0]] = PDF_FOLDER_PATH

    except FileNotFoundError:
        st.error(f"Folder not found: {PDF_folder}")


session_defaults = {
    'selected_boxes': [],
    'page_number': 0,
    'slider_max_value': 100,
    'current_pdf': None,
    'parser_status': True,
    'pdf_instence': None,
    'pdf_selection': None,
    'uploaded_pdf_name': None,
    'uploaded_pdf': None
}

for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


@st.cache_resource
def local_css(css_file_name: str) -> None:
    with open(css_file_name, encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css")  # Load custom CSS


# @st.cache_data
def llama_parser_cache(path: str):
    return parsers_to_list.llama_parse_to_list(path)


@dataclass
class Pdf:
    name: str 
    _folder: str
    path: str = field(init=False)
    page_number: int = field(init=False)


    def __post_init__(self) -> None:
        try:
            if self.name.lower().endswith('.pdf'):
                self.name = self.name[:-4]  # Remove '.pdf'
            self.path = os.path.join(self._folder, f'{self.name}.pdf')
            reader = PdfReader(self.path)
            self.page_number = len(reader.pages)
  
        except Exception as e:
            raise ValueError(f"Failed to read PDF at {self.path}: {e}") from e
        

    @st.cache_data
    def pypdf_pdf_to_text(self, page_numer: int) -> str:
        return parsers_by_page_number.pypdf_parse_page(self.path, page_numer)
    
    @st.cache_data
    def pymupdf_pdf_to_text(self, page_numer):
        return parsers_by_page_number.pymupdf_parse_page(self.path, page_numer)
    
    @st.cache_data
    def pymupdf4llm_pdf_to_text(self, page_numer):
        return parsers_by_page_number.pymupdf4llm_parse_page(self.path, page_numer)
    
    @st.cache_data
    def pytesseract_pdf_to_text(self, page_numer):
        return parsers_by_page_number.pytesseract_parse_page(self.path, page_numer+1)
    
    @st.cache_data
    def aspose_pdf_to_text(self, page_numer):
        return parsers_by_page_number.aspose_parse_page(self.path, page_numer)
    
    def llama_parser_to_text(self, page_numer):
        doc, time_exe= llama_parser_cache(self.path)
        text = doc[page_numer].text[:300000]
        return text, time_exe


def change_image_preview(folder, pdf_name, page_number):
    if st.session_state.pdf_selection != None:
        pdf = pdfium.PdfDocument(f"{os.path.join(folder,pdf_name)}.pdf")
        page = pdf[st.session_state.page_number]
        pil_image = page.render(scale=1).to_pil()
        st.image(pil_image, caption=f"Page {st.session_state.page_number+1} of selected PDF")


def handle_pdf_upload():
    if st.session_state['uploaded_file'] is not None:
        st.session_state['uploaded_pdf_name'] = 'uploaded pdf'
        user_pdf_path = os.path.join(user_pdf_folder_path,"uploaded pdf.pdf")
        st.session_state.pdf['uploaded pdf'] = user_pdf_folder_path
        with open(user_pdf_path, "wb") as f:
            f.write(st.session_state['uploaded_file'].getbuffer())

        if 'uploaded pdf' not in st.session_state.pdf_names:
            st.session_state.pdf_names.append('uploaded pdf')

    else:
        # Detect if the file was removed (by checking if it's no longer in the uploader)
        if st.session_state['uploaded_pdf_name'] in st.session_state['pdf_names']:
            st.session_state['pdf_names'].remove(st.session_state['uploaded_pdf_name'])
            st.session_state['uploaded_pdf_name'] = None


def callback():
    if st.session_state.pdf_selection is not None:
        st.session_state.parser_status = False
        st.session_state.page_number = 0
    else:
        st.session_state.parser_status = True


with st.sidebar:

    st.sidebar.selectbox(
        label="select the PDF you want to parse",
        options=st.session_state.pdf_names,
        index=None,
        key='pdf_selection',
        on_change=callback(),
        )


    if st.session_state.pdf_selection is not None:
        st.session_state.pdf_instence = Pdf(name=st.session_state.pdf_selection, _folder=st.session_state.pdf[st.session_state.pdf_selection])
        st.session_state.slider_max_value = st.session_state.pdf_instence.page_number
        if st.session_state.slider_max_value >1:
            st.session_state.page_number = st.sidebar.slider("Select the page number",
                    min_value=1,
                    max_value=st.session_state.slider_max_value,
                    value=1,
                    step=1, 
                    key="page_number_ara", 
                    on_change=callback(),
                ) -1 
                   
        change_image_preview(st.session_state.pdf[st.session_state.pdf_selection], st.session_state.pdf_selection, st.session_state.page_number)


    for label in box_labels:
        # Create a checkbox for each label
        checked = label in st.session_state.selected_boxes  # Check if this box is already selected
        if st.sidebar.checkbox(label, value=checked, disabled=st.session_state.parser_status):
            # Add the selected box to the list
            if label not in st.session_state.selected_boxes:
                st.session_state.selected_boxes.append(label)
        else:
            # Remove the box if unchecked
            if label in st.session_state.selected_boxes:
                st.session_state.selected_boxes.remove(label)
    

    st.file_uploader("Upload your own PDF, use only PDF files",
                    accept_multiple_files=False,
                    type=['pdf'],
                    key='uploaded_file',
                    on_change=handle_pdf_upload,
                    )



options = {
    'pypdf': 'pypdf_pdf_to_text',
    'pymupdf': 'pymupdf_pdf_to_text',
    'pymupdf4llm': 'pymupdf4llm_pdf_to_text',
    'pytesseract': 'pytesseract_pdf_to_text',
    'aspose': 'aspose_pdf_to_text',
    'llama_parser': 'llama_parser_to_text'
}


# CSS to apply RTL direction
rtl_css = """
<style>
.rtl-text {
    direction: rtl;
    text-align: right;
}
</style>
"""

# Inject the CSS into the app
st.markdown(rtl_css, unsafe_allow_html=True)
n_cols = len(st.session_state.selected_boxes)
if n_cols > 0 and st.session_state.pdf_selection is not None:
    columns = st.columns(n_cols, gap='small')

    for idx, option in enumerate(st.session_state.selected_boxes):
        if hasattr(st.session_state.pdf_instence, options[option]):
            method = getattr(st.session_state.pdf_instence, options[option])
            modified_df, execution_time = method(page_numer=st.session_state.page_number)
            return_text = modified_df
            with columns[idx]:
                columns[idx].markdown(
                      f"""
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <h2 style='margin: 0;'>{st.session_state.selected_boxes[idx]}</h2>
                            <span style='font-size: 1.5em; color: red;'>{execution_time} sec</span>
                        </div>
                        """,  
                    unsafe_allow_html=True
                    )               
                st.markdown(f'<div class="rtl-text">{return_text}</div>',unsafe_allow_html=True)
                
else:
    st.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <h1 style="font-size: 32px; font-weight: bold; color: #FF6347;">No PDF or parser Selected!</h1>
            <p style="font-size: 18px; color: #E0E0E0;">
                Please follow these steps:
            </p>
            <ol style="text-align: left; display: inline-block; font-size: 18px; color: #D3D3D3;">
                <li>Choose a PDF from the dropdown list on the left or upload your own PDF.</li>
                <li>Select the parsers to analyze the chosen PDF.</li>
            </ol>
            <p style="font-size: 18px; color: #E0E0E0;">
                Once you've done this, the parser options will be available here.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )