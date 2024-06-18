from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter()

# 设置模板目录
templates = Jinja2Templates(directory="templates")

