from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.responses import JSONResponse
from mongodb_utils import fetch_all_presses, fetch_press_by_id, insert_press

from models import PressRelease
from gemini_utils import generate_press_description

app = FastAPI()

class PressReleaseCreate(BaseModel):
  title: str
  description: str
  sns_url: str
  uid: str
  image: List[str]

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
  prompt = "Generate test text"
  # prompt = "Generate a press description for the post in {resource.sns_url}"
  if resource.sns_url and not resource.description:
    description_input = generate_press_description(prompt)
  else:
    description_input = resource.description

  press = {
    "title": resource.title,
    "description": description_input,
    "uid": resource.uid,
    "sns_url": resource.sns_url,
    "image": resource.image
  }
  
  inserted_id = insert_press(press)
  return JSONResponse(content={"inserted_id": inserted_id}, status_code=status.HTTP_201_CREATED)
