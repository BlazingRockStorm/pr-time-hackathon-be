from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.responses import JSONResponse
from mongodb_utils import fetch_all_presses, fetch_press_by_id, insert_press
from fastapi.middleware.cors import CORSMiddleware

from models import PressRelease
from gemini_utils import generate_press_input
from x_api_utils import get_x_post

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://prtimes-hackathon-fe.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
  description_prompt = "日本語でこの投稿に基づいてプレスリリースを作成してください。"

  if resource.sns_url and not resource.sns_url.startswith("https://x.com/"):
    raise HTTPException(status_code=400, detail="sns_url must be from X(formerly Twitter)")
  elif resource.sns_url and not resource.description:
    x_post_id = resource.sns_url.split("/status/")[-1]
    x_data = get_x_post(x_post_id)

    if x_data:
      try:
        x_text = x_data['data']['text']
        description_input = generate_press_input(description_prompt + x_text)
        image_urls = [media['url'] for media in x_data['includes']['media']]
        image_input = resource.image + image_urls
      except KeyError:
          print("Error: Could not find 'text' in the response. The API response structure might have changed.")
          print(json.dumps(tweet_data, indent=4)) #Show the response for debugging
          return None
    else:
        print("Failed to retrieve tweet.")
        return None
  else:
    description_input = resource.description
    image_input = resource.image

  if not resource.title:
    title_input = generate_press_input("日本語で一文で以下の記事にタイトルをお付けください" + description_input)
  else:
    title_input = resource.title

  press = {
    "title": title_input,
    "description": description_input,
    "uid": resource.uid,
    "sns_url": resource.sns_url,
    "image": image_input
  }
  
  inserted_id = insert_press(press)
  return JSONResponse(content={"inserted_id": inserted_id}, status_code=status.HTTP_201_CREATED)
