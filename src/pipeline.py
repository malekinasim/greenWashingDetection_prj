from src.pdf_processor import PDFProcessor
from src.extractors.pymupdf_extractor import PyMuPDFExtractor
from src.extractors.opencv_extractor import OpenCVExtractor
from src.rgbDetector.base_rgb_detector import RgbDetector
from src.utils.file_utils import ensure_directory_exists
from src.utils.pdf_file_utils import pdfFileUtils
import os
import pandas as pd

class PDFPipeline:
    def __init__(self, pdf_folder, image_folder,output_folder, method='PYMUPDF'):
        self.pdf_folder = pdf_folder
        self.image_folder = os.path.join(image_folder, "pymupdf" if method=="PYMUPDF" else "opencv")
        self.method = method
        self.output_folder=os.path.join(output_folder, "pymupdf" if method=="PYMUPDF" else "opencv")
        ensure_directory_exists(self.image_folder)
        ensure_directory_exists(self.output_folder)
       
    def _add_to_excel_data_frame(self,all_data):
        file_path=os.path.join(self.output_folder, "output.xlsx")
        data = pd.DataFrame(all_data, columns=["Company", "Year",
                                               "sector","Size",
                                                "Organization_type",
                                                "Sec_SASB", "Region",
                                                "Country","OECD",
                                                "english_non_english", 
                                                "Image Path",
                                                "Title", 
                                                "Author",
                                                "Creation Date",
                                                "Creator",
                                                "modification Date",
                                                "Subject",
                                                "Keywords","pdf Language",
                                                "Red %", "Green %", "Blue %"
                                                #   ,"detected Object",
                                                #   "detected nature Obj",
                                                #   "detected nature object count"
                                                ])
        data.to_excel(file_path, index=False)
 
    def process_pdfs(self,extract_cover_image): 
        all_data=[] 
        for pdf_path in pdfFileUtils().get_pdf_files(self.pdf_folder):
            processor = PDFProcessor(pdf_path)
            extractor = PyMuPDFExtractor(processor, self.image_folder,extract_cover_image) if self.method == 'PYMUPDF' else OpenCVExtractor(processor, self.image_folder,extract_cover_image)
            images = extractor.extract_images()
            for image_path in images :
                rgbDetector=RgbDetector(image_path)  
                all_data.append([processor.company, processor.year,
                                 processor.sector,processor.size,
                                 processor.organization_type,
                                 processor.sec_sasb,processor.region,
                                 processor.country,processor.oecd,
                                 processor.english_non_english ,
                                 str(image_path),
                                 processor.metadata.title,
                                 processor.metadata.author,
                                 processor.metadata.creationDate,
                                 processor.metadata.creator,
                                 processor.metadata.modDate,
                                 processor.metadata.subject,
                                 processor.metadata.keywords,
                                 processor.language,
                                 rgbDetector.red_percentage,
                                 rgbDetector.green_percentage,
                                 rgbDetector.blue_percentage])
            self._add_to_excel_data_frame(all_data)         
            print(f"Extracted {len(images)} images from {pdf_path}")

