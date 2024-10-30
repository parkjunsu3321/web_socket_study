from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Set up the Jinja2 template directory
templates = Jinja2Templates(directory="templates")

class RoomCreateRequest(BaseModel):
    title: int

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요한 도메인으로 제한하는 것이 보안에 좋습니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ws_user = []
ws_group = {}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Render a template file, for example `main_page.html`
    return templates.TemplateResponse("main_page.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/group_select", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("group_select.html", {"request": request})

@app.get("/group_create", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("group_create.html", {"request": request})

@app.get("/a", response_class=HTMLResponse)
async def a_page(request: Request, room_id: str):
    return templates.TemplateResponse("a.html", {"request": request, "room_id": room_id})

@app.websocket("/ws/notice_board")
async def websocket_notice(websocket: WebSocket):
    await websocket.accept()
    ws_user.append(websocket)
    while True:
        data = await websocket.receive_text()
        for wb in ws_user:
            if wb is not websocket:
                await wb.send_text(data)

@app.websocket("/ws/{client_id}")
async def websocket_group(websocket: WebSocket, client_id: int):
    await websocket.accept()
    try:
        ws_group[client_id].append(websocket)
        while True:
            data = await websocket.receive_text()
            for wb in ws_group[client_id]:
                if wb is not websocket:
                    await wb.send_text(data)
    except AttributeError:
        return {"error": "None 포인터 오류"}

@app.get("/get_group")
async def get_group():
    return list(ws_group.keys())

@app.post("/create_group")
async def create_group(payload: RoomCreateRequest):
    ws_group[payload.title] = []
    return True

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)