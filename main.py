from fastapi import FastAPI
from mongodb_utils import fetch_all_presses, fetch_press_by_id

from models import PressRelease

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/press_releases")
async def get_all_presses():
    presses = fetch_all_presses()
    return presses

@app.get("/press_releases/{id}")
async def get_press_by_id(id: str):
    press = fetch_press_by_id(id)
    return press