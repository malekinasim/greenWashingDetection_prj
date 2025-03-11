from pathlib import Path
from src.utils.file_utils import ensure_directory_exists
import hashlib
import cv2
from skimage.metrics import structural_similarity as ssim
import os
import numpy as np
class ImageExtractor:
    def __init__(self, processor, output_folder,extract_cover=True):
        self.processor = processor
        self.output_folder = Path(output_folder)
        ensure_directory_exists(output_folder)
        self.extract_cover=extract_cover

    def _calculate_image_hash(self,image_bytes):
        if len(image_bytes) == 0 or image_bytes is None:
            return None   
        if isinstance(image_bytes, str):
            image_bytes = image_bytes.encode("utf-8")  # Convert to bytes
        if isinstance(image_bytes, np.ndarray):
            image_bytes = image_bytes.tobytes() # Convert to bytes  
        if not isinstance(image_bytes, bytes):
            return None
        return hashlib.md5(image_bytes).hexdigest()

    def _calculate_image_similarity(self, image_path1, image_path2):
        try:
            #load the images in grayscale

            img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

            #if one of the images could not be loaded
            if img1 is None or img2 is None:
                print(f"Error: One of the images could not be loaded. Paths: {image_path1}, {image_path2}")
                return 0

            #check if the images have the same size
            if img1.shape!=img2.shape:
                #get the minimum size of the images
                min_height = min(img1.shape[0], img2.shape[0])
                min_width = min(img1.shape[1], img2.shape[1])

                #change the size of the images to the minimum size
                img1 = cv2.resize(img1, (min_width, min_height), interpolation=cv2.INTER_AREA)
                img2 = cv2.resize(img2, (min_width, min_height), interpolation=cv2.INTER_AREA)

            # return the Structural Similarity Index (SSI) between two images
            score, _ = ssim(img1, img2, full=True,win_size=3)
            return score
        except Exception as e:
            print(f"Error calculating image similarity: {e}")
            return 0


    def _calculate_image_Overlap(self, image_path1, image_path2):
        try:
            #load the images in grayscale
            img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

            #check if the images have the same size
            if img1 is None or img2 is None:
                print(f"error cannot loaded images {image_path1}, {image_path2}")
                return 0

            h1, w1 = img1.shape
            h2, w2 = img2.shape

            # check size of the images
            if h1 >= h2 and w1 >= w2:
                source_img, template_img = img1, img2
                source_path, template_path = image_path1, image_path2
            elif h2 >= h1 and w2 >= w1:
                source_img, template_img = img2, img1
                source_path, template_path = image_path2, image_path1
            else:
                # if the size of the images are not compatible
                source_img, source_path = img1, image_path1
                template_img, template_path = img2, image_path2

                #check if the size of the template image is larger than the source image
                if template_img.shape[0] > source_img.shape[0] or template_img.shape[1] > source_img.shape[1]:
                    scale_w = source_img.shape[1] / template_img.shape[1]
                    scale_h = source_img.shape[0] / template_img.shape[0]
                    scale_factor = min(scale_w, scale_h)
                    new_width = int(template_img.shape[1] * scale_factor)
                    new_height = int(template_img.shape[0] * scale_factor)
                    template_img = cv2.resize(template_img, (new_width, new_height), interpolation=cv2.INTER_AREA)

            
            if template_img.shape[0] > source_img.shape[0] or template_img.shape[1] > source_img.shape[1]:
                print(f"error: the size of the template image is larger than the source image. Paths: {source_path}, {template_path}")
                return None, None

            #execute template matching
            result = cv2.matchTemplate(source_img, template_img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= 0.8:
                return source_path, template_path
            else:
                return None, None

        except Exception as e:
            print(f"خطا در محاسبه شباهت تصاویر: {e}")
            return None, None



    def _calculate_histogram_similarity(self, image_path1, image_path2):
        try :  
            img1 = cv2.imread(image_path1)
            img2 = cv2.imread(image_path2)
            #if one of the images could not be loaded
            if img1 is None or img2 is None:
                print(f"Error: One of the images could not be loaded. Paths: {image_path1}, {image_path2}")
                return 0

            hist1 = cv2.calcHist([img1], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([img2], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])

            hist1 = cv2.normalize(hist1, hist1).flatten()
            hist2 = cv2.normalize(hist2, hist2).flatten()
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)  # Compare histograms 
            return similarity
        except Exception as e:
            print(f"Error calculating histogram similarity: {e}")
            return 0


    def _is_duplicated_image(self, image_path, extracted_images):
        for extracted_image in extracted_images:
            if(extracted_image!=image_path):
                ssim_similarity = self._calculate_image_similarity(image_path, extracted_image)
                # histogram_similarity=self._calculate_histogram_similarity(image_path,extracted_image)
                if ssim_similarity > 0.7 :
                    return True
            
        return False
    
    
    def _have_full_overLap(self, image_path, extracted_images):
        samll_image_paths=[]
        for extracted_image in extracted_images:
            large_img,small_img = self._calculate_image_Overlap(image_path, extracted_image)
            if large_img is not None and small_img is not None:
               samll_image_paths.append(small_img)
            
        return samll_image_paths
    
    def _create_output_directory(self):
        """Create output directory for saving images."""
        try:
            dir_path = os.path.join(self.output_folder, f"{self.processor.company}_{self.processor.year}")
            ensure_directory_exists(dir_path)
            return dir_path
        except Exception as e:
            print(f"Error creating directory {self.output_folder}: {e}")
            return None

    def extract_images(self):
        raise NotImplementedError("Subclasses must implement extract_images()")
