from PIL import Image
import numpy as np

class RgbDetector:
    def __init__(self, image_path):
        self.red_percentage,self.green_percentage,self.blue_percentage = self._get_rgb_percentage(image_path)
        

    def _get_rgb_percentage(self,image_path):
        total_r, total_g, total_b = 0, 0, 0

        image = Image.open(image_path).convert("RGB")
        image_array = np.array(image)

        total_r += np.sum(image_array[:, :, 0])
        total_g += np.sum(image_array[:, :, 1])
        total_b += np.sum(image_array[:, :, 2])
        total_intensity = total_r + total_g + total_b
        r_percent = (total_r / total_intensity) * 100
        g_percent = (total_g / total_intensity) * 100
        b_percent = (total_b / total_intensity) * 100
        return r_percent,g_percent,b_percent