from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from config.config import TRANSLATE_TITLE

router = APIRouter()


# 设置模板目录
templates = Jinja2Templates(directory="templates/translate")


# 跳转到翻译页面
@router.get("/translate", response_class=HTMLResponse)
async def redirect_translate(request: Request):
    return templates.TemplateResponse("translateSelect.html", {"request": request, "data": TRANSLATE_TITLE})

