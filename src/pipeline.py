from src.pdf_processor import PDFProcessor
from src.extractors.pymupdf_extractor import PyMuPDFExtractor
from src.extractors.opencv_extractor import OpenCVExtractor
from src.extractors.sparepdf_extractor import SparePdfExtractor
from src.extractors.combined_extractor import CombinedExtractor
from src.rgbDetector.base_rgb_detector import RgbDetector 
from src.greenwashing_detector.GreenwashingDetector import GreenwashingDetector
from src.utils.file_utils import ensure_directory_exists
from src.utils.pdf_file_utils import PdfFileUtils  
import os
from src.config import SELECTED_SECTORS, SELECTED_YEARS, RDS_FILE_PATH
import pandas as pd

class PDFPipeline:
    def __init__(self, pdf_folder, image_folder, output_folder, method='PYMUPDF'):
        self.pdf_folder = pdf_folder
        self.image_folder = os.path.join(image_folder, method)
        self.method = method
        self.output_folder = os.path.join(output_folder, method)
        ensure_directory_exists(self.image_folder)
        ensure_directory_exists(self.output_folder)

    def _add_to_excel_dataframe(self, all_data):
        file_path = os.path.join(self.output_folder, "output.xlsx")
        data = pd.DataFrame(all_data, columns=["Company", "Year", "Sector", "Size",
                                               "Organization_Type", "Sec_SASB", "Region", 
                                               "Country", "OECD", "English_Non_English", 
                                               "Image_Path", "Title", "Author", 
                                               "Creation_Date", "Creator", "Modification_Date", 
                                               "Subject", "Keywords", "PDF_Language", 
                                               "Red_Percentage", "Green_Percentage", "Blue_Percentage", 
                                               "Green_Brightness", "Green_Contrast", 
                                               "Greenwashing_Result", "Greenwashing_Score"])
        data.to_excel(file_path, index=False)

    def _get_extractor(self, extract_cover_image, processor):
        if self.method == 'PYMUPDF':
            extractor = PyMuPDFExtractor(processor, self.image_folder, extract_cover_image)
        elif self.method == 'OPENCV':
            extractor = OpenCVExtractor(processor, self.image_folder, extract_cover_image)
        elif self.method == 'SPAREPDF':
            extractor = SparePdfExtractor(processor, self.image_folder, extract_cover_image)
        else:
            extractor = CombinedExtractor(processor, self.image_folder, extract_cover_image)

        return extractor

    def process_pdfs(self, extract_cover_image):
        all_data = []  # List to store all extracted data
        pdfFileUtils=PdfFileUtils()
        pdf_paths=pdfFileUtils.get_pdf_files(self.pdf_folder)
        for pdf_path in pdf_paths:
            processor = PDFProcessor(pdf_path)
            extractor = self._get_extractor(extract_cover_image, processor)
            images = extractor.extract_images()

            for image_path in images:
                try:
                    rgb_detector = RgbDetector(image_path)
                    greenwashing_detector = GreenwashingDetector(rgb_detector=rgb_detector)  
                    all_data.append([processor.company, processor.year, processor.sector, processor.size,
                                    processor.organization_type, processor.sec_sasb, processor.region,
                                    processor.country, processor.oecd, processor.english_non_english,
                                    str(image_path), processor.metadata.title, processor.metadata.author,
                                    processor.metadata.creationDate, processor.metadata.creator,
                                    processor.metadata.modDate, processor.metadata.subject,
                                    processor.metadata.keywords, processor.language,
                                    rgb_detector.red_percentage, rgb_detector.green_percentage,
                                    rgb_detector.blue_percentage, rgb_detector.green_brightness,
                                    rgb_detector.green_contrast, greenwashing_detector.greenWashing_result,
                                    greenwashing_detector.greenWashing_score])
                    #print(f"Extracted {len(images)} images from {pdf_path}")
                except Exception as e:
                  print(f"Error processing {image_path  }")
                  print(e)
    
        # Add data to Excel after processing all PDFs (for better performance)
        self._add_to_excel_dataframe(all_data)
        print(f'''the code check {pdfFileUtils.count_of_pdf_files_in_directory(self.pdf_folder)}
 count pdf  files and there was {pdfFileUtils.count_of_ivalid_pdf_files(self.pdf_folder)}
 count invalid pdf files and we select {len(pdf_paths)} count pdf of from these sector : {SELECTED_SECTORS}
 and these years {SELECTED_YEARS} ''')
