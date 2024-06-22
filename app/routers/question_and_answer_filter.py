from pydantic import BaseModel
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from config.config import QA_FILTER_TITLE
from app.services import question_and_answer_filter

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates/qaFilter")

class DatasetMarkRequest(BaseModel):
    name: str
    currentIndex: int

# 跳转到问答筛选页面
@router.get("/qaFilter", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("qaFilterSelect.html", {"request": request, "data": QA_FILTER_TITLE})


# 响应问答筛选的数据
@router.get("/qaFilter/data")
async def read_data(page: int = Query(1, alias="page"), size: int = Query(10, alias="size")):
    start = (page - 1) * size
    end = start + size
    data = question_and_answer_filter.query_data()
    for i in range(100):
        data.extend(question_and_answer_filter.query_data())
    paged_data = data[start:end]
    page_count = len(data) / 10 if (len(data) / 10) > 0 else 1
    return JSONResponse({"data": paged_data,"currentPage": page, "totalItems": len(data), "pageCount": page_count })


@router.get("/qaFilter/mark/{anno_dataset}", response_class=HTMLResponse)
async def mark_data(request: Request, anno_dataset: str):
    # 根据文件夹数据进行处理
    data = {
        "title": QA_FILTER_TITLE,
        "dataset": anno_dataset
    }
    return templates.TemplateResponse("qaFilterAnnotation.html", {"request": request, "data": data})


@router.post("/qaFilter/sync")
async def sync_data(request: DatasetMarkRequest):
    dataset_name = request.name
    return {"message": f"Dataset '{dataset_name}' syn successfully"}


@router.post("/qaFilter/get_data")
async def get_data(request: DatasetMarkRequest):
    print(request.name)
    print(request.currentIndex)
    data = {
        "images": [
            {
                "url": "http://127.0.0.1:8080/image/2022-06-30-small/XWKJ-1212122001_3f0131ba-111f-11ed-8e03-0242ac110004_01_131.jpg",
                "question": "问题内容1",
                "answer": "回答内容1"
            },
            {
                "url": "http://127.0.0.1:8080/image/2022-06-30-small/XWKJ-1212122001_c5bcd5e6-5973-11ed-aff3-0242ac110004_01_205.jpg",
                "question": "问题内容2",
                "answer": "回答内容2"
            },
            {
                "url": "http://127.0.0.1:8080/image/2022-06-30-small/ZGTT-1717124001_47e1cbecd2584ff483f2e6a78290a7c326b51446469b4e5980546380f8e1d567_01_001.jpg",
                "question": "问题内容3",
                "answer": "回答内容3"
            }
        ],
        "currentIndex": 0,
        "totalImages": 3
    }
    return JSONResponse(content=data)