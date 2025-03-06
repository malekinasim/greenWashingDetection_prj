import numpy as np
import cv2

class RgbDetector:
    #green-bound 35-85
    _lower_green = np.array([35, 40, 40])
    _upper_green = np.array([85, 255, 255])
    #blue-bound 90-130
    _lower_blue = np.array([90, 50, 50])
    _upper_blue = np.array([130, 255, 255])

    #red first bound 0-10
    _lower_red1 = np.array([0, 50, 50])
    _upper_red1 = np.array([10, 255, 255])
    #red second bound 170-180
    _lower_red2 = np.array([170, 50, 50])
    _upper_red2 = np.array([180, 255, 255])

    def __init__(self, image_path):
        image = cv2.imread(image_path)
        self.image_path = image_path
        self.green_percentage = self._calculate_green_percentage(image)
        self.blue_percentage = self._calculate_blue_percentage(image)
        self.red_percentage = self._calculate_red_percentage(image)
        self.green_brightness = self._calculate_green_brightness(image)
        self.green_contrast = self._calculate_green_contrast(image)

    def _get_Color_Mask(self,hsv, lower_bound, upper_bound): 
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        return mask   
    def _calculate_color_percentage(self,image, lower_bound, upper_bound):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = self._get_Color_Mask(hsv, lower_bound, upper_bound)
        color_pixels = np.count_nonzero(mask)
        total_pixels = image.shape[0] * image.shape[1]
        return (color_pixels / total_pixels) * 100
    
    def _calculate_green_percentage(self,image):
        return self._calculate_color_percentage(image, self._lower_green, self._upper_green)
   
    def _calculate_blue_percentage(self,image):
        return self._calculate_color_percentage(image, self._lower_blue, self._upper_blue)
    
    def _calculate_red_percentage(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self._lower_red1, self._upper_red1)
        mask2 = cv2.inRange(hsv, self._lower_red2, self._upper_red2)
        mask = mask1 + mask2    
        red_pixels = np.count_nonzero(mask)
        total_pixels = image.shape[0] * image.shape[1]
        return (red_pixels / total_pixels) * 100
    
    def _calculate_green_brightness(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask=self._get_Color_Mask(hsv,self._lower_green,self._upper_green)
        v_channel = hsv[:, :, 2]  # get value channel  as brightness
        if len(v_channel) or len(v_channel[mask > 0]) == 0:
          return 0
        brightness_mean= np.mean(v_channel[mask > 0])  # calculate mean of brightness for all green pixels
        return (brightness_mean / 255) * 100  # normalize brightness to 0-100 scale
    
    def _calculate_green_contrast(self,image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask=self._get_Color_Mask(hsv,self._lower_green,self._upper_green)
        masked_gray = hsv[mask > 0]
        if len(masked_gray) == 0:
            return 0
        return (np.max(masked_gray) - np.min(masked_gray)) / 255 * 100