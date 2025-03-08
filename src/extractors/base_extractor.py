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
            similarity = self._calculate_image_similarity(image_path, extracted_image)
            if similarity > 0.7:
                return True
            
        return False
    
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
