from pathlib import Path
from src.utils.file_utils import ensure_directory_exists
import hashlib

class ImageExtractor:
    def __init__(self, processor, output_folder,extract_cover=True):
        self.processor = processor
        self.output_folder = Path(output_folder)
        ensure_directory_exists(output_folder)
        self.extract_cover=extract_cover

    def _calculate_image_hash(self,image_bytes):
        """Calculate the hash of an image file to detect duplicates."""
        return hashlib.md5(image_bytes).hexdigest()

    def extract_images(self):
        raise NotImplementedError("Subclasses must implement extract_images()")
