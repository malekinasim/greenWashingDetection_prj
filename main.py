from  src.pipeline import PDFPipeline
from src.config import PDF_FOLDER_PATH,IMAGE_FOLDER_PATH,EXCEL_OUTPUT_FOLDER_PATH
def main():
   PDFPipeline(PDF_FOLDER_PATH, IMAGE_FOLDER_PATH,EXCEL_OUTPUT_FOLDER_PATH, method='PYMUPDF').process_pdfs(True)
   PDFPipeline(PDF_FOLDER_PATH, IMAGE_FOLDER_PATH,EXCEL_OUTPUT_FOLDER_PATH, method='OPENCV').process_pdfs(True)
#
#  Run the pipelin

main()