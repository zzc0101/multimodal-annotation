from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from config.config import QA_FILTER_TITLE
from app.services import question_and_answer_filter

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates/qaFilter")

# 跳转到问答筛选页面
@router.get("/qaFilter", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("qaFilterSelect.html", {"request": request, "data": QA_FILTER_TITLE})


# 响应问答筛选的数据
@router.get("/qaFilter/data", response_class=HTMLResponse)
async def read_data(page: int = Query(1, alias="page"), size: int = Query(10, alias="size")):
    start = (page - 1) * size
    end = start + size
    data = question_and_answer_filter.query_data()
    paged_data = data[start:end]
    page_count = len(data) / 10 if (len(data) / 10) > 0 else 1
    return JSONResponse({"data": paged_data, "total": len(data), "pageCount": page_count })


@router.get("/qaFilter/data/{anno_dataset}", response_class=HTMLResponse)
async def sync_data(anno_dataset: str):
    # 根据文件夹数据进行处理
    
    return JSONResponse({"message": anno_dataset})
