import cv2
import numpy as np
from pdf2image import convert_from_path
from src.extractors.base_extractor import ImageExtractor
from src.utils.file_utils import ensure_directory_exists
from src.config import IMAGE_SIZE_THRESHOALD_COEF

class OpenCVExtractor(ImageExtractor):
    def extract_images(self):
        if(self.extract_cover):
          images = convert_from_path(self.processor.pdf_path, first_page=1, last_page=1)
        else:
          images = convert_from_path(self.processor.pdf_path)
        extracted_images = []
        

        dir_path=f"{self.output_folder}\\{self.processor.company}_{self.processor.year}"
        ensure_directory_exists(dir_path)

        for i, image in enumerate(images):
            extracted_hashes=set()
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            _, binary_gray = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            gray_contours, _ = cv2.findContours(binary_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            v = hsv[:, :, 2]
            _, binary_v = cv2.threshold(v, 200, 255, cv2.THRESH_BINARY_INV)
            contours_v, _ = cv2.findContours(binary_v, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            image_index=1
            for contour in (gray_contours if len(contours_v) < len(gray_contours) else (contours_v)):
              x, y, w, h = cv2.boundingRect(contour)
              img_height, img_width = img_cv.shape[:2]
              min_width = img_width * IMAGE_SIZE_THRESHOALD_COEF
              min_height = img_height * IMAGE_SIZE_THRESHOALD_COEF
              if w < min_width or  h < min_height:
                continue
              
              extracted_image = img_cv[y:y+h, x:x+w]

              image_bytes = cv2.imencode('.png', extracted_image)[1].tobytes()
              image_hash =self._calculate_image_hash(image_bytes)
              if image_hash in extracted_hashes:
                      continue 
                     
              extracted_hashes.add(image_hash)

              image_filename = f"{dir_path}\\opencv_p{i+1}_i{image_index}.png"
              cv2.imwrite(str(image_filename), extracted_image)
              extracted_images.append(image_filename)  
              image_index+=1
        return extracted_images
