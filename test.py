import os
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import pandas as pd
from langdetect import detect
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
# Load DETR model and processor
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
NATURE_OBJECT = {"tree", "river", "leaf", "grass", "flower", "water", "mountain", "cloud", "bird"}

def get_detect_nature_objects(image_path):
    """Detect nature objects in the image using DETR."""
    if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None

    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)

        # Convert outputs to bounding boxes and labels
        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

        nature_found = set()

        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            label_name = model.config.id2label[label.item()]
            if label_name in NATURE_OBJECT:
                nature_found.add(label_name)

        return list(nature_found) if nature_found else None
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None
    
# get_detect_nature_objects("data/extracted_images/COMBINE/ZonaFrancadeBarranquilla_2016/pymupdf_p1_i1.jpeg")

# get_detect_nature_objects("data/extracted_images/COMBINE/ZonaFrancadeBarranquilla_2016/pymupdf_p1_i2.jpeg")

# get_detect_nature_objects("data/extracted_images/COMBINE/ZonaFrancadeBarranquilla_2016/pymupdf_p1_i3.jpeg")

# get_detect_nature_objects("data/extracted_images/COMBINE/ZonaFrancadeBarranquilla_2016/pymupdf_p1_i4.jpeg")

get_detect_nature_objects("data/extracted_images/COMBINE/TNTExpress_2014/opencv_p1_i1.png")



