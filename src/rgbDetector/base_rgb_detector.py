import numpy as np
import cv2
from src.utils.image_util import convert_to_bgrhsv

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
        self.image_path = image_path
        self.green_percentage = self._calculate_green_percentage(image_path)
        self.blue_percentage = self._calculate_blue_percentage(image_path)
        self.red_percentage = self._calculate_red_percentage(image_path)
        self.green_brightness = self._calculate_green_brightness(image_path)
        self.green_contrast = self._calculate_green_contrast(image_path)

    def _get_Color_Mask(self,hsv, lower_bound, upper_bound): 
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        return mask   
    
    def _calculate_color_percentage(self,image_path, lower_bound, upper_bound):
        image,hsv = convert_to_bgrhsv(image_path)
        
        if image is None or hsv is None:
            print(f"[WARNING] Failed to load image: {image_path}")
            return 0
        
        mask = self._get_Color_Mask(hsv, lower_bound, upper_bound)

        color_pixels = np.count_nonzero(mask)
        total_pixels = image.shape[0] * image.shape[1]
        if total_pixels == 0:
             return 0
        return (color_pixels / total_pixels) * 100
    
    def _calculate_green_percentage(self,image_path):
        return self._calculate_color_percentage(image_path, self._lower_green, self._upper_green)
   
    def _calculate_blue_percentage(self,image_path):
        return self._calculate_color_percentage(image_path, self._lower_blue, self._upper_blue)
    
    def _calculate_red_percentage(self,image_path):
        image,hsv =convert_to_bgrhsv(image_path)
        
        if image is None or hsv is None:# check if image is loaded successfully
            print(f"[WARNING] Failed to load image: {image_path}")
            return 0
        
        # get masks for red pixels
        mask1 = cv2.inRange(hsv, self._lower_red1, self._upper_red1)
        mask2 = cv2.inRange(hsv, self._lower_red2, self._upper_red2)
        # combine masks
        mask = cv2.bitwise_or(mask1, mask2)
    
        # calculate percentage of red pixels
        red_pixels = np.count_nonzero(mask)

        total_pixels =  image.shape[0] * image.shape[1]
        if total_pixels == 0:
             return 0

        return (red_pixels / total_pixels) * 100
    
    def _get_Mask_brightness_VChannel(self,image_path,lower_green,upper_green):
    # get brightness values for green pixels
       
        image,hsv = convert_to_bgrhsv(image_path)  # convert image to hsv
        if image is None or hsv is None:# check if image is loaded successfully
            print(f"[WARNING] Failed to load image: {image_path}")
            return np.array([])
        

        # get mask for green pixels
        mask=self._get_Color_Mask(hsv,lower_green,upper_green)

        # get brightness values for green pixels
        v_channel = hsv[:, :, 2]

        # apply mask to v_channel
        masked_v_channel  = v_channel[mask > 0]

        return masked_v_channel
    
    def _calculate_green_brightness(self,image_path):
        masked_v_channel=self._get_Mask_brightness_VChannel(image_path,self._lower_green,self._upper_green)
        if masked_v_channel.size == 0:  
          return 0    
         
        brightness_mean= np.mean(masked_v_channel)  # calculate mean of brightness for all green pixels
        return (brightness_mean / 255) * 100  # normalize brightness to 0-100 scale
    
    def _calculate_green_contrast(self,image_path):
        masked_v_channel  = self._get_Mask_brightness_VChannel(image_path,self._lower_green,self._upper_green)
        if masked_v_channel.size == 0:  
          return 0
        
        # calculate contrast for green pixels
        return (np.max(masked_v_channel.astype(np.float32)) - np.min(masked_v_channel.astype(np.float32))) / 255 * 100