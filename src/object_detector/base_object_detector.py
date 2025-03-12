

class ObjectDetector:
    
    def __init__(self, model,  nature_objects):
        # Check if method is 'DETR' and processor is None, raise an error
        self.model = model
        self.nature_objects = nature_objects
        
    
    def get_detect_objects(self, image_path):
         raise NotImplementedError("Subclasses must implement extract_images()")
