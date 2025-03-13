from ultralytics import YOLO
import os
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

if __name__ == '__main__':

    model = YOLO("yolov8x.pt")  

    model.train(data="data\\model\\OCR Greewashing.v4i.yolov8\\data.yaml",
    epochs=80,
    batch=8,
    lr0=0.001,  
    momentum=0.9,
    weight_decay=0.0005,
    device="cuda"  
)

