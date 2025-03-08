from src.extractors.base_extractor import ImageExtractor
from spire.pdf.common import *
from spire.pdf import *
from PIL import Image
import io
from src.config import IMAGE_SIZE_THRESHOLD_COEF
import os
class SparePdfExtractor(ImageExtractor):
    def extract_images(self):   
        pages_to_process = [0] if self.extract_cover else range(self.processor.doc.page_count)
       
        dir_path =self._create_output_directory()
        if dir_path is None:
            return []
        
        try:
            doc = PdfDocument(self.processor.pdf_path)
        except Exception as e:
            print(f"Error opening PDF document: {e}")
            return []
        images= self._process_images(doc, pages_to_process, dir_path) 
        try:
            doc.Dispose()  # Ensure resources are properly freed
        except Exception as e:
            print(f"Error disposing of PDF document: {e}")
        
        return images
       
    def _process_images(self, doc, pages_to_process, dir_path):
        images = []
        for page_index in pages_to_process:
            try:
                page = doc.Pages.get_Item(page_index)
                images.extend(self._extract_images_from_page(page, page_index, dir_path))
                  
            except Exception as e:
                print(f"Error processing page {page_index + 1}: {e}")

        return images
    
   
    def _extract_images_from_page(self, page, page_index, dir_path):
                """Extract images from a given page."""
                images = []
                page_width = page.Size.Width
                page_height = page.Size.Height
                extracted_hashes = set()
                imageHelper = PdfImageHelper()
                imageInfos = imageHelper.GetImagesInfo(page)
                img_index = 1           
                for imageInfo in imageInfos:
                    try:
                        image = imageInfo.Image
                        img_width, img_height = imageInfo.Bounds.Width, imageInfo.Bounds.Height
                        
                        # Check if the image is large enough
                        if  self._is_image_small(img_width, img_height, page_width, page_height):
                            continue
                        
                        image_bytes = image.ToArray()  # If Spire.PDF provides this method
                        image_hash = self._calculate_image_hash(image_bytes)
                        
                        if image_hash is not None and image_hash in extracted_hashes:
                            continue
                        if(image_hash is not None):
                          extracted_hashes.add(image_hash)
                        image_path=self._save_image(image_bytes, dir_path, page_index, img_index)
                        
                        images.append(image_path)
                        img_index += 1
                    except Exception as e:
                        print(f"Error processing image on page {page_index + 1}: {e}")
                return images

    def _save_image(self, image_bytes, dir_path, page_index, img_index):
        try:   
            image_pil = Image.open(io.BytesIO(image_bytes))
            image_ext = image_pil.format.lower() 
            image_path = os.path.join(dir_path,f"sparepdf_p{page_index + 1}_i{img_index}.{image_ext}")                
            # Save the image
            image_pil.save(image_path)
            return image_path
        except Exception as e:
            print(f"Error saving image: {e}")
            return None

    def _is_image_small(self, img_width, img_height, page_width, page_height):
        """Check if the image dimensions are above the threshold."""
        min_width = page_width * IMAGE_SIZE_THRESHOLD_COEF
        min_height = page_height * IMAGE_SIZE_THRESHOLD_COEF
        return not (img_width >= min_width and img_height >= min_height)
