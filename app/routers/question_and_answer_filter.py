import json
from pydantic import BaseModel
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.services import question_and_answer_filter, operator_record
from config import config
from app.utils import anno_type

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates/qaFilter")

class DatasetMarkRequest(BaseModel):
    name: str
    currentIndex: int

class DatasetSynRequest(BaseModel):
    datasetName: str

class DatasetSaveRequest(BaseModel):
    datasetName: str
    fileName: str
    currentIndex: int
    questionValue: str
    answerValue: str
    correctFlag: bool


@router.get("/qaFilter", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    跳转到问答筛选页面。
    """
    return templates.TemplateResponse("qaFilterSelect.html", {"request": request, "data": config.QA_FILTER_TITLE})


@router.get("/qaFilter/data")
async def read_data(page: int = Query(1, alias="page"), size: int = Query(10, alias="size")):
    """
    响应问答筛选的分页数据。
    """
    start = (page - 1) * size
    end = start + size
    data = question_and_answer_filter.query_data()
    paged_data = data[start:end]
    page_count = max(len(data) // size, 1)
    
    return JSONResponse({"data": paged_data, "currentPage": page, "totalItems": len(data), "pageCount": page_count})


@router.get("/qaFilter/mark/{anno_dataset}", response_class=HTMLResponse)
async def mark_data(request: Request, anno_dataset: str):
    """
    根据给定的注释数据集标记数据。
    """
    # 加载上次的标注记录数据
    record_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    
    # 为模板准备数据
    data = {
        "title": config.QA_FILTER_TITLE,
        "dataset": anno_dataset,
        "currentIndex": 0
    }

    if record_data:
        load_data = operator_record.query_entry(record_data, anno_dataset, anno_type.get_attribute('filter'))
        if load_data:
            # 根据加载的数据获取当前索引
            data['currentIndex'] = question_and_answer_filter.get_current_index(config.QA_ANNOTATION_SAVE_PATH ,anno_dataset, load_data['preview'])

    return templates.TemplateResponse("qaFilterAnnotation.html", {"request": request, "data": data})


@router.post("/qaFilter/sync")
async def sync_data(request: DatasetSynRequest):
    """
    同步问答筛选数据。
    """
    sync_result = question_and_answer_filter.sync_data(datasetName=request.datasetName)
    return JSONResponse(content=sync_result)


@router.post("/qaFilter/get_data")
async def get_data(request: DatasetMarkRequest):
    """
    根据当前索引获取标注数据。
    """
    data = question_and_answer_filter.get_anno_data(request.name, request.currentIndex)
    return JSONResponse(content=data)


@router.post('/qaFilter/save_data')
async def save_data(request: DatasetSaveRequest):
    """
    保存标注数据。
    """
    question_and_answer_filter.save_anno_data(json.loads(request.json()))
    return {"message": "数据保存成功！"}
