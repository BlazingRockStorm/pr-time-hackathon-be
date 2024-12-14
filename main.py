from fastapi import FastAPI
from pydantic import BaseModel
from mongodb_utils import fetch_all_presses, fetch_press_by_id, insert_press

from models import PressRelease

app = FastAPI()

class PressReleaseCreate(BaseModel):
  title: str
  description: str
  uid: str
  image: list[str]

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

@app.post("/press_releases")
async def create_press(resource: PressReleaseCreate):
  press = {
    "title": resource.title,
    "content": resource.content,
    "uid": resource.uid,
    "image": resource.image
  }
  
  inserted_id = insert_press(press)
  return JSONResponse(content={"inserted_id": inserted_id}, status_code=status.HTTP_201_CREATED)
