from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from config.config import QA_TITLE

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates/qa")


# 跳转到问答筛选页面
@router.get("/qa", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("qaSelect.html", {"request": request, "data": QA_TITLE})


# 响应问答标注的分页数据
@router.get("/qa/data")
async def read_data(page: int = Query(1, alias="page"), size: int = Query(10, alias="size")):
    start = (page - 1) * size
    end = start + size
    data = []
    paged_data = data[start:end]
    page_count = len(data) / 10 if (len(data) / 10) > 0 else 1
    return JSONResponse({"data": paged_data,"currentPage": page, "totalItems": len(data), "pageCount": page_count })

