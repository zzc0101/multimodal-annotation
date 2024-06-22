import cv2, io
import numpy as np
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter()

def resize_image(image_path: str, target_width: int, target_height: int) -> bytes:
    # 读取图像
    image = cv2.imread(image_path)
    
    # 调整图像大小到1080p
    resized_image = cv2.resize(image, (target_width, target_height))
    
    # 将图像转换为字节流
    _, img_encoded = cv2.imencode('.jpg', resized_image)
    return img_encoded.tobytes()

@router.get("/image/{dataset}/{name}", response_class=StreamingResponse)
async def stream_image(dataset: str, name: str):
    img_bytes = resize_image("D:/test/img/" + dataset + '/' + name, 1920, 1080)
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/jpeg")
