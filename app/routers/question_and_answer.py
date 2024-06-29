import os
from pydantic import BaseModel
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from config import config
from app.services import question_and_answer, operator_record
from app.utils import anno_type

# 创建路由器实例
router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates/qa")

# 定义请求模型
class DatasetSynRequest(BaseModel):
    datasetName: str

class DatasetMarkRequest(BaseModel):
    name: str
    currentIndex: int

class DatasetSaveRequest(BaseModel):
    datasetName: str
    fileName: str
    currentIndex: int
    questionValue: str
    answerValue: str


# 跳转到问答筛选页面
@router.get("/qa", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    返回问答筛选页面。
    """
    return templates.TemplateResponse("qaSelect.html", {"request": request, "data": config.QA_TITLE})


# 响应问答标注的分页数据
@router.get("/qa/data")
async def read_data(page: int = Query(1, alias="page"), size: int = Query(10, alias="size")):
    """
    获取分页后的问答标注数据。
    """
    start = (page - 1) * size
    end = start + size
    data = question_and_answer.query_data()
    paged_data = data[start:end]
    page_count = len(data) // size + (1 if len(data) % size > 0 else 0)
    return JSONResponse({"data": paged_data, "currentPage": page, "totalItems": len(data), "pageCount": page_count})


# 跳转到问答标注页面
@router.get("/qa/mark/{anno_dataset}", response_class=HTMLResponse)
async def mark_data(request: Request, anno_dataset: str):
    """
    返回问答标注页面，并加载上次的标注数据。
    """
    record_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    data = {
        "title": config.QA_FILTER_TITLE,
        "dataset": anno_dataset,
        "currentIndex": 0
    }
    if record_data:
        load_data = operator_record.query_entry(record_data, anno_dataset, anno_type.get_attribute('anno'))
        if load_data:
            data['currentIndex'] = question_and_answer.get_current_index(anno_dataset, load_data['preview'])
    return templates.TemplateResponse("qaAnnotation.html", {"request": request, "data": data})


# 问答筛选同步接口
@router.post("/qa/merge")
async def merge_data(request: DatasetSynRequest):
    """
    同步标注数据。
    """
    response = question_and_answer.merge_data(datasetName=request.datasetName)
    return JSONResponse(content=response)


# 问答标注获取数据
@router.post("/qa/get_data")
async def get_data(request: DatasetMarkRequest):
    """
    获取指定数据集和索引的标注数据。
    """
    data = question_and_answer.get_anno_data(request.name, request.currentIndex)
    return JSONResponse(content=data)


# 保存问答标注数据
@router.post('/qa/save_data')
async def save_data(request: DatasetSaveRequest):
    """
    保存标注数据。
    """
    question_and_answer.save_anno_data(request.dict())
    return {"message": "保存成功！"}
