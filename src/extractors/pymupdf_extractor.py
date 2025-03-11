import fitz
import os
from src.extractors.base_extractor import ImageExtractor
from src.config import IMAGE_SIZE_THRESHOLD_COEF


class PyMuPDFExtractor(ImageExtractor):
    def extract_images(self):

        pages_to_process = [0] if self.extract_cover else range(self.processor.doc.page_count)
        
        dir_path = self._create_output_directory()
        if dir_path is None:
            return []
        extracted_images = self._process_images(pages_to_process, dir_path)
        return extracted_images
    
    def _process_images(self, pages_to_process,dir_path):
        images = []
        # Process each page in the PDF fileand extract imagesfrom it
        for page_index in pages_to_process:
            try:
                page = self.processor.doc.load_page(page_index)
                images.extend(self._extract_images_from_page(page, page_index, dir_path))
            except Exception as e:
                print(f"Error processing page {page_index + 1} for pdf file {self.processor.pdf_path}: {e}")
                continue
        return images

    def _extract_images_from_page(self, page, page_index, dir_path):
        """Extract images from a given page."""
        extracted_hashes = set()
        images = []
        img_index = 1
        page_width, page_height = page.rect.width, page.rect.height
        
        for img in page.get_images(full=True):
            try:
                xref = img[0]
                base_image = self.processor.doc.extract_image(xref)
                #rm
                if  self._is_image_small(base_image, page_width, page_height):
                    continue  # Skip small images
                
               
                #check if image is extracted correctly
                if(base_image is None or base_image['image'] is None):
                    continue

                image_hash = self._calculate_image_hash(base_image['image'])
                #remove duplicate images
                if image_hash is not None and  image_hash in extracted_hashes:
                    continue  # Skip already extracted images
                if(image_hash is not None):
                 extracted_hashes.add(image_hash)
                image_path = self._save_image(base_image, dir_path, page_index, img_index)
                img_index += 1
                images.append(image_path)
            except Exception as e:
                print(f"Error extracting image from page {page_index + 1}, image {img_index}: {e}")
        return images

    def _is_image_small(self, img, page_width, page_height):
        """Check if the image dimensions are above the threshold."""
        try:
            min_width = page_width * IMAGE_SIZE_THRESHOLD_COEF
            min_height = page_height * IMAGE_SIZE_THRESHOLD_COEF
            return not (img['width'] >= min_width and img['height'] >= min_height)
        except Exception as e:
            print(f"Error checking image size: {e}")
            return False

    def _save_image(self, base_image, dir_path, page_index, img_index):
        """Save the image to the specified directory."""
        try:
            image_path = os.path.join(dir_path,f"pymupdf_p{page_index + 1}_i{img_index}.{base_image['ext']}")
            with open(image_path, "wb") as img_file:
                img_file.write(base_image["image"])
                img_file.close()
            return image_path
        except Exception as e:
            print(f"Error saving image {img_index} on page {page_index + 1}: {e}")
            return None
