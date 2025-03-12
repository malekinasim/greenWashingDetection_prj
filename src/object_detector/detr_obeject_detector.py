import os
from PIL import Image
import torch
from src.object_detector.base_object_detector import ObjectDetector

class DTER_ObjectDetector(ObjectDetector):
    
    def __init__(self, model, processor, nature_objects):
        # Check if method is 'DETR' and processor is None, raise an error
        if processor is None:
            raise ValueError("You should provide a processor for DETR model.")
        self.processor = processor
        super(model,nature_objects)
       
    def get_detect_objects(self, image_path):
        """Detect nature objects using DETR."""
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return [], []

        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt")
            outputs = self.model(**inputs)

            # Convert outputs to bounding boxes and labels
            target_sizes = torch.tensor([image.size[::-1]])
            results = self.processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

            nature_found = set()
            all_found = set()
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                label_name = self.model.config.id2label[label.item()]
                all_found.add(label_name)
                if label_name in self.nature_objects:
                    nature_found.add(label_name)

            return list(nature_found) if len(nature_found) != 0 else [], list(all_found) if len(all_found) else []
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return [], []

   
# Example usage:
# Initialize the ObjectDetector with the model, processor, nature objects, and method
# Assuming `model`, `processor`, and `NATURE_OBJECT` are defined
# detector = ObjectDetector(model, processor, NATURE_OBJECT, 'DETR')

# # Call the methods to detect objects in an image
# image_path = 'path_to_your_image.jpg'
# nature_objects_v1, all_objects_v1 = detector.get_detect_objects(image_path)
# nature_objects_v2, all_objects_v2 = detector.get_detect_objects(image_path)

# print("Nature Objects (DETR):", nature_objects_v1)
# print("All Detected Objects (DETR):", all_objects_v1)
