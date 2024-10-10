from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
import torch

app = FastAPI()

# YOLO 모델 로드 (사전 학습된 모델 사용)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

@app.get("/")
def read_root():
    return {"message": "FastAPI Image Processing Server is running!"}

# 이미지 업로드 엔드포인트
@app.post("/upload/image")
async def process_image(file: UploadFile = File(...)):
    # 업로드된 파일을 메모리에서 읽어들이기
    contents = await file.read()

    # 이미지 파일을 OpenCV 형식으로 변환
    np_array = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # YOLO 모델로 객체 탐지 수행
    results = model(image)

    # 탐지된 객체 정보 추출
    detected_objects = []
    for result in results.xyxy[0]:
        detected_objects.append({
            "class": model.names[int(result[5])],
            "bbox": result[:4].tolist(),  # 좌표 추출
            "confidence": result[4].item()  # 신뢰도 추출
        })

    # 객체 탐지 결과를 JSON으로 반환
    return {"objects": detected_objects}
