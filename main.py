import os
import uvicorn
from config.config import Server_Port
from fastapi import FastAPI
from routers import question_and_answer, translation
from fastapi.responses import HTMLResponse

app = FastAPI()

# 响应首页
@app.get("/", response_class=HTMLResponse)
def redirect_url():
    file_path = os.path.join(os.path.dirname(__file__), "templates/index.html")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content, status_code=200)
    return HTMLResponse(content="File not found", status_code=404)


app.include_router(question_and_answer.router)
app.include_router(translation.router)


if "__main__" == __name__:
    # gr.mount_gradio_app(app, create_gradio(), path=CUSTOM_PATH)
    uvicorn.run(app, host="0.0.0.0", port=Server_Port)