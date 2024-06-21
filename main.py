import uvicorn
from config.config import Server_Port
from fastapi import FastAPI, Request
from app.routers import question_and_answer, translation, question_and_answer_filter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

app = FastAPI()

# 设置静态文件路径，指向 static 文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板目录
templates = Jinja2Templates(directory="templates")

# 响应首页
@app.get("/", response_class=HTMLResponse)
def redirect_url(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "server_port": Server_Port})
    # file_path = os.path.join(os.path.dirname(__file__), "templates/index.html")
    # if os.path.exists(file_path):
    #     with open(file_path, "r") as file:
    #         html_content = file.read()
    #     html_content = html_content.replace('Server_Port', str(Server_Port))
    #     return HTMLResponse(content=html_content, status_code=200)
    # return HTMLResponse(content="File not found", status_code=404)


app.include_router(question_and_answer.router)
app.include_router(translation.router)
app.include_router(question_and_answer_filter.router)


if "__main__" == __name__:
    # gr.mount_gradio_app(app, create_gradio(), path=CUSTOM_PATH)
    uvicorn.run(app, host="0.0.0.0", port=Server_Port)