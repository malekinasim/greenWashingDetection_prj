from src.extractors.base_extractor import ImageExtractor
from src.utils.file_utils import ensure_directory_exists
from   spire.pdf.common import *
from  spire.pdf import * 
from PIL import Image
import io
from src.config import IMAGE_SIZE_THRESHOALD_COEF
class SparePdfExtractor(ImageExtractor):
    def extract_images(self):   
        images = []
        imageHelper = PdfImageHelper()
        pages_to_process = [0] if self.extract_cover else range(self.processor.doc.page_count)
        dir_path=f"{self.output_folder}\\{self.processor.company}_{self.processor.year}"
        ensure_directory_exists(dir_path)
        doc = PdfDocument(self.processor.pdf_path)
        for page_index in pages_to_process:
            page = doc.Pages.get_Item(page_index)
            page_width = page.Size.Width
            page_height = page.Size.Height
            extracted_hashes = set()
            imageInfos= imageHelper.GetImagesInfo(page)
            img_index=1
            for imageInfo in imageInfos:    
                image = imageInfo.Image
                 
                img_width, img_height = imageInfo.Bounds.Width, imageInfo.Bounds.Height
                min_width = page_width * IMAGE_SIZE_THRESHOALD_COEF
                min_height = page_height * IMAGE_SIZE_THRESHOALD_COEF

                if img_width < min_width or img_height < min_height:
                    continue  
                image_bytes = image.ToArray()  # If Spire.PDF provides this method
                image_hash =self._calculate_image_hash(image_bytes)
                if image_hash in extracted_hashes:
                      continue  
                
                extracted_hashes.add(image_hash)
                image_pil = Image.open(io.BytesIO(image_bytes))
                image_ext = image_pil.format.lower() 
                image_path =f"{dir_path}\\sparepdf_p{page_index+1}_i{img_index}.{image_ext}"
                image.Save(image_path) 
                images.append(image_path)
                img_index+=1         
        doc.Dispose()   
        return images
