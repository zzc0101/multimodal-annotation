import json
from pydantic import BaseModel
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from config import config
from app.services import question_and_answer, operator_record
from app.utils import anno_type

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates/qa")


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
    return templates.TemplateResponse("qaSelect.html", {"request": request, "data": config.QA_TITLE})


# 响应问答标注的分页数据
@router.get("/qa/data")
async def read_data(page: int = Query(1, alias="page"), size: int = Query(10, alias="size")):
    start = (page - 1) * size
    end = start + size
    data = question_and_answer.query_data()
    paged_data = data[start:end]
    page_count = len(data) / 10 if (len(data) / 10) > 0 else 1
    return JSONResponse({"data": paged_data,"currentPage": page, "totalItems": len(data), "pageCount": page_count })


@router.get("/qa/mark/{anno_dataset}", response_class=HTMLResponse)
async def mark_data(request: Request, anno_dataset: str):
    # 获取上次标注数据
    record_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    # 根据文件夹数据进行处理
    data = {
        "title": config.QA_FILTER_TITLE,
        "dataset": anno_dataset,
        "currentIndex": 0
    }
    if not record_data is None:
        load_data = operator_record.query_entry(record_data, anno_dataset, anno_type.get_attribute('anno'))
        if not load_data is None:
            # 根据文件查询当前文件在列表中的下标
            data['currentIndex'] = question_and_answer.get_current_index(anno_dataset, load_data['preview'])
    return templates.TemplateResponse("qaAnnotation.html", {"request": request, "data": data})


# 问答筛选同步接口
@router.post("/qa/sync")
async def merge_data(request: DatasetSynRequest):
    return JSONResponse(content=question_and_answer.merge_data(datasetName=request.datasetName))


# 问答标注获取数据
@router.post("/qa/get_data")
async def get_data(request: DatasetMarkRequest):
    data = question_and_answer.get_anno_data(request.name, request.currentIndex)
    return JSONResponse(content=data)


# 保存问答标注数据
@router.post('/qa/save_data')
async def save_data(request: DatasetSaveRequest):
    question_and_answer.save_anno_data(json.loads(request.json()))
    return {"message": "保存成功！"}
