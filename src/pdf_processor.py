import fitz
from pathlib import Path
from src.utils.language_utils import detect_pdf_language
from src.utils.pdf_file_utils import pdfFileUtils
class Metadata:
    def __init__(self, metadata):
        self.title=metadata.get("title", "Unknown")
        self.author=metadata.get("author", "Unknown")
        self.creationDate=metadata.get("creationDate", "Unknown")
        self.creator=metadata.get("creator", "Unknown")
        self.modDate=metadata.get("modDate", "Unknown")
        self.subject=metadata.get("subject", "Unknown")
        self.keywords=metadata.get("keywords", "Unknown")
        
class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.file_name,self.company, self.year = self.extract_pdf_info()
        self.metadata= Metadata(self.doc.metadata)
        self.language = self.detect_language()
        selected_pdf_infos=pdfFileUtils().get_selected_pdf_infos()
        if(len(selected_pdf_infos)>0):
            self.sector=selected_pdf_infos[self.file_name][0]
            self.size=selected_pdf_infos[self.file_name][1]
            self.organization_type=selected_pdf_infos[self.file_name][2]
            self.sec_sasb=selected_pdf_infos[self.file_name][3]
            self.region=selected_pdf_infos[self.file_name][4]
            self.country=selected_pdf_infos[self.file_name][5]
            self.oecd=selected_pdf_infos[self.file_name][6]
            self.english_non_english=selected_pdf_infos[self.file_name][7] 

    def extract_pdf_info(self):
        file_name= Path(self.pdf_path).stem
        parts=file_name.split("_")
        return file_name,parts[0], parts[1] if len(parts) > 1 else "Unknown"

    def detect_language(self):
        text = " ".join([page.get_text() for page in self.doc])
        return detect_pdf_language(text)

