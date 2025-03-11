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
            images = convert_from_path(self.processor.pdf_path, dpi=300, first_page=1, last_page=1) if self.extract_cover else convert_from_path(self.processor.pdf_path ,dpi=300)
        except Exception as e:
            print(f"[ERROR] Failed to open PDF: {self.processor.pdf_path}, Error: {e}")
            return []

        dir_path = self._create_output_directory()
        if dir_path is None:
            return [] 
        # extracted_images = self._process_images(images)
        extracted_images=self._save_pdf_page_images(images)

        return extracted_images
    def _save_pdf_page_images(self, images):
        extracted_images = []     
        for i, image in enumerate(images):
            try:   
                dir_path=os.path.join(self.output_folder, f"{self.processor.company}_{self.processor.year}")
                image_path = os.path.join(dir_path,f"Opencv_i{i+1}.png")
                image.save(image_path, 'PNG')
                extracted_images.append(image_path)
            except Exception as e:
                print(f"[ERROR] Error processing page {i+1} in {self.processor.pdf_path}: {e}")
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

            
            # gray_contours = self._remove_overlapping_contours(gray_contours,img_cv)
            # contours_v = self._remove_overlapping_contours(contours_v,img_cv)

        except Exception as e:
            print(f"[ERROR] Error finding contours: {e}")
            return [], []
        
        return gray_contours, contours_v

    def _remove_overlapping_contours(self, contours, img_cv):
        filtered_contours = []       
        for c1 in contours:
            x1, y1, w1, h1 = cv2.boundingRect(c1)
            keep = True
            
            for c2 in contours:
                if c1 is c2:
                    continue
                x2, y2, w2, h2 = cv2.boundingRect(c2)
                # بررسی اینکه c1 کاملاً داخل c2 هست یا نه
                # بررسی همپوشانی (اگر c1 درون c2 باشد، حذف شود)
                if x1 >= x2 and y1 >= y2 and (x1 + w1) <= (x2 + w2) and (y1 + h1) <= (y2 + h2):
                        # استخراج دو ناحیه و مقایسه رنگ
                        x1, y1, w1, h1 = cv2.boundingRect(c1)
                        x2, y2, w2, h2 = cv2.boundingRect(c2)

                        img1 = img_cv[y1:y1+h1, x1:x1+w1]
                        img2 = img_cv[y2:y2+h2, x2:x2+w2]

                        if self._are_images_similar(img1, img2):
                            keep = False
                            break
                        

            if keep:
                filtered_contours.append(c1)

        return filtered_contours
    def _are_images_similar(self,img1, img2, threshold=0.9):
        hist1 = cv2.calcHist([img1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist2 = cv2.calcHist([img2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()

        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return similarity > threshold

    def _process_contour(self, img_cv, contour, extracted_hashes, page_index, image_index):
        try:
            x, y, w, h = map(int, cv2.boundingRect(contour))  # Get the bounding box of the contour
            
            # Check if the image is too small
            img_height, img_width = img_cv.shape[:2]
            min_width = img_width * IMAGE_SIZE_THRESHOLD_COEF
            min_height = img_height * IMAGE_SIZE_THRESHOLD_COEF

            if w < min_width or h < min_height:
                return None

            extracted_image = img_cv[y:y+h, x:x+w]

            if extracted_image.size == 0:
                return None

            image_bytes = cv2.imencode('.png', extracted_image)[1].tobytes()
            image_hash = self._calculate_image_hash(image_bytes)

            if image_hash is not None and image_hash in extracted_hashes:
                return None
            if image_hash is not None:
                extracted_hashes.add(image_hash)
            
            image_filename = os.path.join(self.output_folder, f"{self.processor.company}_{self.processor.year}", f"opencv_p{page_index+1}_i{image_index}.png")
            cv2.imwrite(image_filename, extracted_image)

            return image_filename

        except Exception as e:
            print(f"[ERROR] Error processing contour in {self.processor.pdf_path}: {e}")
            return None
