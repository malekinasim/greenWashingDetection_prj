import os
from src.config import SELECTED_SECTORS, SELECTED_YEARS, RDS_FILE_PATH
import pyreadr
import fitz
from src.utils.file_utils import is_dir, get_file_path

class PdfFileUtils:
    _SELECTED_PDF_INFOS = None

    def __init__(self):
        if PdfFileUtils._SELECTED_PDF_INFOS is None:
            PdfFileUtils._SELECTED_PDF_INFOS = self._calc_selected_pdf_infos()

    def get_selected_pdf_infos(self):
        return PdfFileUtils._SELECTED_PDF_INFOS

    
    def _calc_selected_pdf_infos(self):
        result = pyreadr.read_r(RDS_FILE_PATH)  
        df_rds = result[None]  
        print(df_rds.columns)

        selected_sectors = [sector.strip() for sector in SELECTED_SECTORS.split(",")]
        selected_years = [int(year.strip()) for year in SELECTED_YEARS.split(",")]

        df_selected = df_rds[df_rds["Sector"].isin(selected_sectors) & df_rds["Year"].isin(selected_years)]

        return dict(zip(df_selected["file"], zip(
            df_selected["Sector"],
            df_selected["Size"],
            df_selected["Organization_type"],
            df_selected["Sec_SASB"],
            df_selected["Region"],
            df_selected["Country"],
            df_selected["OECD"],
            df_selected["english_non_english"],
            df_selected["Year"]
        )))

    def _is_pdf_valid(self, pdf_path):
        try:
            pdf_file = fitz.open(pdf_path) 
            page_count = pdf_file.page_count
            if page_count == 0:
                print(f"Invalid PDF (no pages): {pdf_path}")
                return False 
            page = pdf_file.load_page(0)
            if not page:
                print(f"Invalid PDF (unable to load the first page): {pdf_path}")
                return False 
            return True
        except Exception as e:
            print(f"Error opening PDF file '{pdf_path}': {e}")  
            return False

    def count_of_pdf_files_in_directory(self,folder_path):
        try:
            # List all files in the directory
            files = os.listdir(folder_path)

            # Filter out only PDF files by checking the extension
            pdf_files = [file for file in files if file.lower().endswith('.pdf')]

            # Return the count of PDF files
            return len(pdf_files)
        
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            return 0
    
    def count_of_ivalid_pdf_files(self,folder_path):
        try:
            # List all files in the directory
            files = os.listdir(folder_path)

            # Filter out only PDF files by checking the extension
            pdf_files = [file for file in files if self._is_pdf_valid(get_file_path(folder_path, file))]

            # Return the count of PDF files
            return len(pdf_files)
        
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            return 0
    
    def count_of_SELECTED_PDF_files(self,folder_path):
        try:
            # List all files in the directory
            files = os.listdir(folder_path)

            # Filter out only PDF files by checking the extension
            pdf_files = [file for file in files if self._is_pdf_valid
                         (get_file_path(folder_path, file)) and 
                         file.lower().endswith('.pdf') and 
                         file in PdfFileUtils._SELECTED_PDF_INFOS]

            # Return the count of PDF files
            return len(pdf_files)
        
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            return 0
        
    def get_pdf_files(self, folder_path):
        if not is_dir(folder_path):
            print(f"Error: PDF folder ({folder_path}) does not exist!")
            return []
        return [get_file_path(folder_path, f) for f in os.listdir(folder_path)
                if f.endswith(".pdf") and self._is_pdf_valid(get_file_path(folder_path, f))
                  and f.replace(".pdf", "") in PdfFileUtils._SELECTED_PDF_INFOS]
