from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates")


# 跳转到问答筛选页面
@router.get("/qa", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("qaSelect.html", {"request": request, "data": "问答筛选"})


