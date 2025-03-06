from pathlib import Path
from src.utils.file_utils import ensure_directory_exists
import hashlib
import cv2
from skimage.metrics import structural_similarity as ssim

class ImageExtractor:
    def __init__(self, processor, output_folder,extract_cover=True):
        self.processor = processor
        self.output_folder = Path(output_folder)
        ensure_directory_exists(output_folder)
        self.extract_cover=extract_cover

    def _calculate_image_hash(self,image_bytes):
        return hashlib.md5(image_bytes).hexdigest()
    
    def _calculate_image_similarity(self, image_path1, image_path2):
        img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

        if img1.shape != img2.shape:
            
            min_height = min(img1.shape[0], img2.shape[0])
            min_width = min(img1.shape[1], img2.shape[1])
            
            img1 = cv2.resize(img1, (min_width, min_height))
            img2 = cv2.resize(img2, (min_width, min_height))

        score, _ = ssim(img1, img2, full=True)
        return score
    

    def _calculate_histogram_similarity(self, image_path1, image_path2):
        img1 = cv2.imread(image_path1)
        img2 = cv2.imread(image_path2)

        hist1 = cv2.calcHist([img1], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
        hist2 = cv2.calcHist([img2], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])

        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()

        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL )  # مقایسه هیستوگرام‌ها
        return similarity
    

    def _is_duplicated_image(self, image_path, extracted_images):
        for extracted_image in extracted_images:
            similarity = self._calculate_image_similarity(image_path, extracted_image)
            if similarity > 0.95:
                return True
            
        return False
    
    def extract_images(self):
        raise NotImplementedError("Subclasses must implement extract_images()")
