from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import List
import uvicorn
from pydantic import BaseModel

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextFile(BaseModel):
    txtfile: str

txtfile_init: str = ""  # 초기값 설정

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

clients: List[WebSocket] = []

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("a.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            for client in clients:
                if client != websocket:
                    await client.send_text(data)
    except Exception:
        clients.remove(websocket)

@app.post("/save_init")
async def save_init(txtfile: TextFile):
    global txtfile_init
    txtfile_init = txtfile.txtfile
    print(txtfile_init)
    
    # 모든 클라이언트에게 업데이트된 내용을 전송
    for client in clients:
        await client.send_text(txtfile_init)

@app.get("/load_txt")
async def load_init():
    if txtfile_init:  # 내용이 있을 때만 전송
        return {"txtfile": txtfile_init}
    return {"txtfile": ""}  # 내용이 없으면 빈 문자열 반환

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)