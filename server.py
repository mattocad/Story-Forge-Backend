from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import backend

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartRequest(BaseModel):
    mode: str

@app.post("/start")
def start_game(req: StartRequest):
    narrative = backend.reset_game(req.mode)
    return {"narrative": narrative}

@app.post("/command")
def command(req: dict):
    user_input = str(req.get("option"))
    narrative = backend.process_command(user_input)
    return {"narrative": narrative}

@app.post("/undo")
def undo_turn():
    narrative = backend.undo_last_turn()
    return {"narrative": narrative}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
