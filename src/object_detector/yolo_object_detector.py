import os
from PIL import Image
import torch
from src.object_detector.base_object_detector import ObjectDetector

class YOLO_ObjectDetector(ObjectDetector):
    def get_detect_objects(self, image_path):
        """Detect nature objects using YOLO method."""
        try:
            results = self.model(image_path)

            nature_found = set()
            all_found = set()

            output_folder = os.path.join(os.path.dirname(image_path), "detect_output")
            os.makedirs(output_folder, exist_ok=True)

            for result in results:
                img = Image.fromarray(result.plot())
                output_path = os.path.join(output_folder, os.path.basename(image_path))
                img.save(output_path)

                boxes = result.boxes.xyxy.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                labels = result.boxes.cls.cpu().numpy()

                for i, label in enumerate(labels):
                    confidence = confidences[i]
                    box = boxes[i]
                    class_name = result.names[int(label)]
                    if class_name in self.nature_objects:
                        nature_found.add(f"Detected {class_name} with confidence {confidence} at {box}")
                    all_found.add(f"Detected {class_name} with confidence {confidence} at {box}")

            return list(all_found) if all_found else [], list(nature_found) if nature_found else []
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return [], []
