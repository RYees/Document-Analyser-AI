from pypdf import PdfReader
from collections import namedtuple
Page = namedtuple("Page", ["id", "page_content", "metadata"])

class FileReader:
    def pdf_reader_to_list_format(file_path):
        reader = PdfReader(file_path)
        pdf_texts = [p.extract_text().strip() for p in reader.pages]
        pdf_texts = [text for text in pdf_texts if text]
        return pdf_texts

    def pdf_reader_to_document_format(file_path):
        reader = PdfReader(file_path)
        pdf_pages = []
        for page_number, page in enumerate(reader.pages):
            page_content = page.extract_text().strip()
            if page_content:
                metadata = {"page_number": page_number}  # Add any additional metadata as needed
                pdf_pages.append(Page(id=page_number, page_content=page_content, metadata=metadata))
        return pdf_pages

