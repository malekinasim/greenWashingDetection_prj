import os
import cv2
from pdf2image import convert_from_path
from src.extractors.base_extractor import ImageExtractor
from src.config import IMAGE_SIZE_THRESHOLD_COEF
from src.utils.file_utils import check_file_exists
from src.utils.image_util import convert_to_cv

class OpenCVExtractor(ImageExtractor):
    def extract_images(self):
        extracted_images = []
        
        
        if not check_file_exists(self.processor.pdf_path):
            return []
    
        try:
            images = convert_from_path(self.processor.pdf_path, first_page=1, last_page=1) if self.extract_cover else convert_from_path(self.processor.pdf_path)
        except Exception as e:
            print(f"[ERROR] Failed to open PDF: {self.processor.pdf_path}, Error: {e}")
            return []

        dir_path = self._create_output_directory()
        if dir_path is None:
            return [] 
        extracted_images = self._process_images(images)

        return extracted_images
 
    def _process_images(self, images):
        extracted_hashes = set()
        extracted_images = []
       

        for i, image in enumerate(images):
            try:
                img_cv = convert_to_cv(image)
                gray_contours, contours_v = self._find_contours(img_cv)

                image_index = 1
                for contour in (gray_contours if len(contours_v) < len(gray_contours) else contours_v):
                    extracted_image = self._process_contour(img_cv, contour, extracted_hashes, i, image_index)
                    if extracted_image is not None:
                        extracted_images.append(extracted_image)
                        image_index += 1
            except Exception as e:
                print(f"[ERROR] Error processing page {i+1} in {self.processor.pdf_path}: {e}")

        return extracted_images

    def _find_contours(self, img_cv):
        
        try:
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            _, binary_gray = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            gray_contours, _ = cv2.findContours(binary_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            v = hsv[:, :, 2]
            _, binary_v = cv2.threshold(v, 200, 255, cv2.THRESH_BINARY_INV)
            contours_v, _ = cv2.findContours(binary_v, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        except Exception as e:
            print(f"[ERROR] Error finding contours: {e}")
            return [], []
        
        return gray_contours, contours_v

    def _process_contour(self, img_cv, contour, extracted_hashes, page_index, image_index):
        
        try:
            # Get the bounding box of the contour and extract the image
            x, y, w, h = map(int, cv2.boundingRect(contour))  # Get the bounding box of the contour
            
            # Check if the image is too small
            img_height, img_width = img_cv.shape[:2]
            min_width = img_width * IMAGE_SIZE_THRESHOLD_COEF
            min_height = img_height * IMAGE_SIZE_THRESHOLD_COEF

            # Check if the extracted image is too small
            if w < min_width or h < min_height :
                return None

            extracted_image = img_cv[y:y+h, x:x+w]

            # Check if the extracted image is empty
            if extracted_image.size == 0:
                return None

            # Check if the extracted image is duplicated
            image_bytes = cv2.imencode('.png', extracted_image)[1].tobytes()
            image_hash = self._calculate_image_hash(image_bytes)

            if image_hash is not None and image_hash in extracted_hashes:
                return None
            if(image_hash is not None):
               extracted_hashes.add(image_hash)
            
            # Save the extracted image
            image_filename = os.path.join(self.output_folder, f"{self.processor.company}_{self.processor.year}", f"opencv_p{page_index+1}_i{image_index}.png")
            cv2.imwrite(image_filename, extracted_image)

            return image_filename

        except Exception as e:
            print(f"[ERROR] Error processing contour in {self.processor.pdf_path}: {e}")
            return None, None
