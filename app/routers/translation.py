from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from config.config import TRANSLATE_TITLE
import json
from app.services import translation, operator_record
from config import config
from pydantic import BaseModel
from app.utils import anno_type
import app.utils.file_util as file_util
import os

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates/translate")


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
    questionValueEn: str
    answerValueEn: str


# 跳转到翻译页面
@router.get("/translate", response_class=HTMLResponse)
async def redirect_translate(request: Request):
    return templates.TemplateResponse("translateSelect.html", {"request": request, "data": TRANSLATE_TITLE})


# 响应问答筛选的分页数据
@router.get("/translate/data")
async def read_data(page: int = Query(1, alias="page"), size: int = Query(10, alias="size")):
    start = (page - 1) * size
    end = start + size
    data = translation.query_data()
    paged_data = data[start:end]
    page_count = len(data) / 10 if (len(data) / 10) > 0 else 1
    return JSONResponse({"data": paged_data, "currentPage": page, "totalItems": len(data), "pageCount": page_count})


@router.get("/translate/mark/{anno_dataset}", response_class=HTMLResponse)
async def mark_data(request: Request, anno_dataset: str):
    # 获取上次标注数据
    record_data = operator_record.load_json(config.OPERATION_RECORD_PATH)
    # 根据文件夹数据进行处理
    data = {
        "title": config.TRANSLATE_TITLE,
        "dataset": anno_dataset,
        "currentIndex": 0
    }
    if record_data is not None:
        load_data = operator_record.query_entry(record_data, anno_dataset, anno_type.get_attribute('translate'))
        if load_data is not None:
            # 根据文件查询当前文件在列表中的下标
            data['currentIndex'] = translation.get_current_index(anno_dataset, load_data['preview'])
    return templates.TemplateResponse("translateAnnotation.html", {"request": request, "data": data})


# 问答筛选同步接口
# @router.post("/translate/sync")
# async def sync_data(request: DatasetSynRequest):
#     data = {}
#     dataset_name = request.datasetName
#     flag = translation.sync_data(datasetName=dataset_name)
#     data['message'] = '同步成功！' if flag else '同步失败！'
#     data['code'] = 200 if flag else 500
#     return JSONResponse(content=data)


# 问答筛选获取数据
@router.post("/translate/get_data")
async def get_data(request: DatasetMarkRequest):
    data = translation.get_anno_data(request.name, request.currentIndex)
    return JSONResponse(content=data)


# 保存问答筛选数据
@router.post('/translate/save_data')
async def save_data(request: DatasetSaveRequest):
    translation.save_anno_data(json.loads(request.json()))

    dataset_name = request.datasetName
    record_file_path = config.OPERATION_RECORD_PATH
    save_file_path = os.path.join(config.TRANSLATE_ANNOTATION_FILE_PATH, config.CHINESE_FOLDER, dataset_name)
    file_util.update_today_count(dataset_name=dataset_name, record_file_path=record_file_path,
                                 save_file_path=save_file_path)
    return {"message": "保存成功！"}
