import fitz
from src.extractors.base_extractor import ImageExtractor
from src.utils.file_utils import ensure_directory_exists
from src.config import IMAGE_SIZE_THRESHOALD_COEF

class PyMuPDFExtractor(ImageExtractor):
    def extract_images(self):
        images = []
        pages_to_process = [0] if self.extract_cover else range(self.processor.doc.page_count)
        dir_path=f"{self.output_folder}\\{self.processor.company}_{self.processor.year}"
        ensure_directory_exists(dir_path)
        for page_index in pages_to_process:
            page = self.processor.doc.load_page(page_index)
            page_width = page.rect.width
            page_height = page.rect.height
            img_index=1
            extracted_hashes = set()
            for img in page.get_images(full=True):
                xref = img[0]
                pix = fitz.Pixmap(self.processor.doc, xref)
                img_width, img_height = pix.width, pix.height
                min_width = page_width * IMAGE_SIZE_THRESHOALD_COEF
                min_height = page_height * IMAGE_SIZE_THRESHOALD_COEF

                if img_width < min_width or img_height < min_height:
                    pix = None  
                    continue  

                base_image = self.processor.doc.extract_image(xref)               
                image_hash =self._calculate_image_hash(base_image['image'])
                if image_hash in extracted_hashes:
                      continue     
                extracted_hashes.add(image_hash)

                image_path =f"{dir_path}\\pymupdf_p{page_index+1}_i{img_index}.{base_image['ext']}"
                with open(image_path, "wb") as img_file:
                    img_file.write(base_image["image"])
                img_index+=1
                images.append(image_path)
        return images
