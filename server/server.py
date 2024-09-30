import socket
import numpy as np
import cv2

# 서버 설정
HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 연결을 허용
PORT = 8000       # 사용할 포트 번호

# 소켓 생성 및 바인드
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print("서버가 클라이언트 연결을 기다리는 중...")

# 클라이언트가 연결되면 데이터 수신
conn, addr = server_socket.accept()
print(f"{addr}와 연결되었습니다.")

# 데이터 수신 및 YOLO 처리 반복
while True:
    data = b""
    payload_size = struct.calcsize("L")
    
    while len(data) < payload_size:
        data += conn.recv(4096)
    
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_msg_size)[0]
    
    while len(data) < msg_size:
        data += conn.recv(4096)
    
    frame_data = data[:msg_size]
    data = data[msg_size:]
    
    # 받은 데이터를 이미지로 변환
    frame = np.frombuffer(frame_data, dtype=np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    
    # YOLO 모델로 이미지 처리 (예시 코드)
    # 여기서 YOLO 모델을 불러와 frame을 처리하면 됨
    # 처리된 결과는 processed_frame이라 가정
    
    # OpenCV로 이미지 보여주기
    cv2.imshow('Received Image', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # YOLO 처리 결과를 클라이언트로 전송
    # conn.sendall(processed_result)
    
conn.close()
server_socket.close()
