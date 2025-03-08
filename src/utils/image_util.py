from PIL import Image
import cv2
import numpy as np

import cv2
import numpy as np
from PIL import Image

def convert_to_bgrhsv(image_path):
    try:
        #read image with OpenCV
        image = cv2.imread(image_path)
        #check if image is in CMYK format and convert to RGB
        if image is None: 
            print(f"[INFO] OpenCV failed to read {image_path}, trying PIL instead.")
            
            #read image with PIL
            img_pil = Image.open(image_path)

            #check if image is in CMYK format and convert to RGB
            if img_pil.mode == "CMYK":
                img_pil = img_pil.convert("RGB")

            #convert PIL image to numpy array and then to BGR format
            image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        # get numpy array of image for return value
        if not isinstance(image, np.ndarray):
            raise ValueError(f"[ERROR] Image conversion failed for {image_path}")

        #convert image to hsv
        img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        return image, img_hsv

    except Exception as e:
        print(f"[ERROR] Error processing {image_path}: {e}")
        return None, None  # RETURN NONE IF ERROR OCCURS


def convert_to_bgr(image_path):
    try:
        img = Image.open(image_path)
        if img.mode == "CMYK":
            img = img.convert("RGB")  # convert CMYK to RGB
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)  #CONVERT TO OPENCV FORMAT
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def convert_to_cv(image):
    try:
        if image.mode == "CMYK":
            img = image.convert("RGB")  #CONVERT CMYK TO RGB
        else:
            img = image
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img_cv  #CONVERT TO OPENCV FORMAT
    except Exception as e:
        print(f"[ERROR] Error converting image to OpenCV format: {e}")
        return None
