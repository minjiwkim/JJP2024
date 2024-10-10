from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
from dotenv import load_dotenv
import os

load_dotenv()
server_ip = os.getenv("SERVER_IP")

app = FastAPI()

# static 디렉토리를 FastAPI에 연결 (이미지 파일을 저장할 디렉토리)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 이미지를 저장할 경로 설정
UPLOAD_DIR = "static/images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 서버가 시작될 때 static/images 폴더를 비우는 함수
def clear_image_folder():
    if os.path.exists(UPLOAD_DIR):
        # 폴더 내의 모든 파일을 삭제
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)  # 파일 삭제
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

# FastAPI 서버가 시작될 때 실행
@app.on_event("startup")
async def startup_event():
    clear_image_folder()  # 서버 실행 시 static/images 폴더를 비우기

# 홈 페이지에서 이미지를 보여주는 HTML을 반환 (1초마다 페이지를 새로고침)
@app.get("/", response_class=HTMLResponse)
def read_root():
    files = os.listdir(UPLOAD_DIR)
    img_tags = "".join([f'<img src="/static/images/{file}" width="300" />' for file in files])
    return f"""
    <html>
        <head>
            <title>Uploaded Images</title>
            <meta http-equiv="refresh" content="5"> <!-- n초마다 페이지를 새로고침 -->
        </head>
        <body>
            <h1>Uploaded Images</h1>
            {img_tags if files else "<p>No images uploaded yet.</p>"}
        </body>
    </html>
    """

# 이미지 업로드 엔드포인트 (클라이언트에서 호출)
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    # 파일 저장 경로 생성
    file_location = f"{UPLOAD_DIR}/{file.filename}"

    # 업로드된 파일을 static/images 폴더에 저장
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"info": f"file '{file.filename}' saved at '{file_location}'"}
