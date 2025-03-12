from src.pdf_processor import PDFProcessor
from src.extractors.pymupdf_extractor import PyMuPDFExtractor
from src.extractors.opencv_extractor import OpenCVExtractor
from src.extractors.sparepdf_extractor import SparePdfExtractor
from src.extractors.combined_extractor import CombinedExtractor
from src.rgbDetector.base_rgb_detector import RgbDetector 
from src.greenwashing_detector.GreenwashingDetector import GreenwashingDetector
from src.utils.file_utils import ensure_directory_exists
from src.utils.pdf_file_utils import PdfFileUtils  
import re
import os
from src.config import SELECTED_SECTORS, SELECTED_YEARS, RDS_FILE_PATH
import pandas as pd
import fnmatch

class PDFPipeline:
    def __init__(self, pdf_folder, image_folder, output_folder, method='PYMUPDF'):
        self.pdf_folder = pdf_folder
        self.image_folder = os.path.join(image_folder, method)
        self.method = method
        self.output_folder = os.path.join(output_folder, method)
        ensure_directory_exists(self.image_folder)
        ensure_directory_exists(self.output_folder)

    def _remove_illegal_chars(self,value):
        """حذف کاراکترهای غیرمجاز از مقدارها"""
        if isinstance(value, str):
            return re.sub(r'[\x00-\x1F]', '', value)  # حذف کاراکترهای غیرمجاز
        return value

    def _add_to_excel_dataframe(self, all_data):
        file_path = os.path.join(self.output_folder, "output.xlsx")

        # بررسی مقدار all_data
        print(f"✅ تعداد رکوردها در all_data: {len(all_data)}")
        if not all_data:
            print("⚠️ خطا: all_data خالی است!")
            return

        # مشخص کردن نام ستون‌ها
        expected_columns = [
            "Company", "Year", "Sector", "Size", "Organization_Type", "Sec_SASB", 
            "Region", "Country", "OECD", "English_Non_English", "Image_Path", "Title", 
            "Author", "Creation_Date", "Creator", "Modification_Date", "Subject", 
            "Keywords", "PDF_Language", "Red_Percentage", "Green_Percentage", 
            "Blue_Percentage", "Green_Brightness", "Green_Contrast", 
            "Greenwashing_Result", "Greenwashing_Score"
        ]

        # تبدیل لیست به DataFrame با ستون‌های مشخص‌شده
        df = pd.DataFrame(all_data, columns=expected_columns)

        # جایگزینی مقادیر NaN با مقدار خالی
        df.fillna('', inplace=True)

        # حذف کاراکترهای غیرمجاز از تمام مقادیر
        df = df.applymap(self._remove_illegal_chars)

        # بررسی ساختار داده‌ها
        print("✅ ۵ سطر اول DataFrame:")
        print(df.head())

        # ذخیره در اکسل
        df.to_excel(file_path, index=False)


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
    def create_output(self):
        image_extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.webp')
        all_data = []  # List to store all extracted data
        

        pdfFileUtils = PdfFileUtils()
        pdf_paths = pdfFileUtils.get_extracted_pdf(self.pdf_folder,self.image_folder)

        for pdf_path in pdf_paths:
            images = []
            processor = PDFProcessor(pdf_path)
            dir_path = os.path.join(self.image_folder, f"{processor.company}_{processor.year}")

            if not os.path.exists(dir_path):
                print(f"Skipping {dir_path}: Directory does not exist")
                continue  # Skip if directory doesn't exist

            # List all files in dir_path
            file_list = os.listdir(dir_path)

            # Filter files with any matching image extension
            images.extend(
                os.path.join(dir_path, filename) 
                for filename in file_list 
                if any(fnmatch.fnmatch(filename, ext) for ext in image_extensions)
            )
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
                        print(f"len: {len(all_data)}")
                        
                    except Exception as e:
                              print(f"Error processing {image_path  }")
                              print(e)
            if(len(all_data)>=500):
                    break
        self._add_to_excel_dataframe(all_data)
#         print(f'''the code check {pdfFileUtils.count_of_pdf_files_in_directory(self.pdf_folder)}
#  count pdf  files and there was {pdfFileUtils.count_of_ivalid_pdf_files(self.pdf_folder)}
#  count invalid pdf files and we select {len(pdf_paths)} count pdf of from these sector : {SELECTED_SECTORS}
#  and these years {SELECTED_YEARS} ''')   

    def process_pdfs(self, extract_cover_image):
        all_data = []  # List to store all extracted data
        pdfFileUtils=PdfFileUtils()
        pdf_paths=pdfFileUtils.get_pdf_files(self.pdf_folder)
        for pdf_path in pdf_paths:
            processor = PDFProcessor(pdf_path)
            extractor = self._get_extractor(extract_cover_image, processor)
            extractor.extract_images()
            self.create_output()
    