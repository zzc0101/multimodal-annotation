import json
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


class DatasetSaveRequest(BaseModel):
    datasetName: str
    fileName: str
    currentIndex: int
    questionValue: str
    answerValue: str
    correctFlag: bool

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
    data = question_and_answer_filter.get_anno_data(request.name, request.currentIndex)
    return JSONResponse(content=data)


@router.post('/qaFilter/save_data')
async def save_data(request: DatasetSaveRequest):
    question_and_answer_filter.save_anno_data(json.loads(request.json()))
    return {"message": "保存成功！"}