import os
from src.extractors.base_extractor import ImageExtractor
from src.extractors.pymupdf_extractor import PyMuPDFExtractor
from src.extractors.opencv_extractor import OpenCVExtractor
from src.extractors.sparepdf_extractor import SparePdfExtractor  

class CombinedExtractor(ImageExtractor):
    def __init__(self, processor, output_folder,extract_cover=True):
        super().__init__(processor, output_folder,extract_cover)
        self.methods = [
            #PyMuPDFExtractor(processor, output_folder,extract_cover),
            OpenCVExtractor(processor, output_folder,extract_cover)#,
            # SparePdfExtractor(processor, output_folder,extract_cover)  
        ]
        
    
    def _calculate_image_hash(self, image_path):
        with open(image_path, 'rb') as img_file:
           return super()._calculate_image_hash(img_file.read())
    
    def extract_images(self):
        extracted_images = []
        
        for extractor in self.methods:
            images = extractor.extract_images()
            extracted_hashes=set()
            for image_path in images:
                img_hash = self._calculate_image_hash(image_path)
                if img_hash not in extracted_hashes:
                  if(not self._is_duplicated_image(image_path, extracted_images)):
                      extracted_hashes.add(img_hash)
                      extracted_images.append(image_path)
                  else:
                      os.remove(image_path)
                else:
                    os.remove(image_path) 
        
        return extracted_images