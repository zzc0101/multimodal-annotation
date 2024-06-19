from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates")

# 假数据集
data = [
    {"id": i, "name": f"User{i}", "age": 20 + i} for i in range(1, 101)
]


# 跳转到问答筛选页面
@router.get("/qaFilter", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("qaFilterSelect.html", {"request": request, "data": "问答筛选"})


# 响应问答筛选的数据
@router.get("/qaFilter/data", response_class=HTMLResponse)
async def read_data(page: int = Query(1, alias="page"), size: int = Query(10, alias="size")):
    start = (page - 1) * size
    end = start + size
    paged_data = data[start:end]
    page_count = len(data) / 10 if (len(data) / 10) > 0 else 1
    return JSONResponse({"data": paged_data, "total": len(data), "pageCount": page_count })
