from fastapi import FastAPI, File, UploadFile
import os
import torch
import shutil
import cv2
from PIL import Image
import numpy as np

app = FastAPI()

# YOLO 모델 로드 (사전 학습된 모델)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# 업로드된 파일을 저장할 디렉토리
UPLOAD_DIR = './uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 루트 경로 추가
@app.get("/")
def read_root():
    return {"message": "FastAPI server is running!"}

# 이미지 업로드 엔드포인트 (JPG 이미지 파일 처리)
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # 업로드된 JPG 파일을 서버에 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 객체 탐지 수행
    results = perform_object_detection(file_path)
    
    return {"objects": results}

# 객체 탐지 수행 함수 (JPG 이미지 파일)
def perform_object_detection(file_path: str):
    # 이미지를 로드하여 YOLO 모델로 객체 탐지 수행
    img = Image.open(file_path)
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)  # PIL 이미지를 OpenCV 형식으로 변환
    
    # YOLO 모델로 객체 탐지 수행
    results = model(img)
    
    # 탐지된 객체 정보 추출
    detected_objects = []
    for result in results.xyxy[0]:
        detected_objects.append({
            "class": model.names[int(result[5])],
            "bbox": result[:4].tolist(),
            "confidence": result[4].item()
        })

    # 객체 탐지 결과 로그 출력
    if not detected_objects:
        print("No objects detected.")
    else:
        for obj in detected_objects:
            objectClass = obj["class"]
            confidence = obj["confidence"]
            bbox = obj["bbox"]
            print(f"Detected Object, Class: {objectClass}, Confidence: {confidence}, BBox: {bbox}")

    return detected_objects