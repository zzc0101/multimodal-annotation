import io
from app.utils import img_file
from fastapi import APIRouter, Request
from config import config
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/image/{dataset}/{name}", response_class=StreamingResponse)
async def stream_image(dataset: str, name: str):
    img_bytes = img_file.resize_image(config.IMAGE_PATH + "/" + dataset + '/' + name, 1920, 1080)
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/jpeg")
