from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
import struct
import pickle
from PIL import Image
import io
# uvicorn main:app --reload
# main은 파일 이름 (예: 파일 이름이 main.py이면 main).
# app은 FastAPI 애플리케이션 객체 이름입니다.

app = FastAPI()

# 루트 경로 확인을 위한 엔드포인트
@app.get("/")
def read_root():
    return {"message": "FastAPI Image Processing Server is running!"}

# 이미지 처리 엔드포인트
@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    # 업로드된 파일을 메모리에서 읽어들이기
    contents = await file.read()
    
    # 이미지 파일을 OpenCV 형식으로 변환
    np_array = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # OpenCV로 받은 이미지를 처리 (예: 간단한 전처리나 가공)
    # 여기에 YOLO 모델 등을 적용 가능
    processed_image = process_with_yolo(image)

    # 결과를 JSON 형식으로 반환 (예시: 이미지 크기 반환)
    return {"message": "Image processed", "width": processed_image.shape[1], "height": processed_image.shape[0]}

def process_with_yolo(image):
    """
    여기에 YOLO 모델을 적용하여 이미지를 처리하는 함수를 추가할 수 있습니다.
    예시로 이미지를 그대로 반환하는 함수입니다.
    """
    # YOLO 모델 처리 코드 추가
    # 결과 처리 후 원하는 데이터를 반환
    return image  # 현재는 처리 없이 그대로 반환
