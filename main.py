from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.responses import JSONResponse
from mongodb_utils import fetch_all_presses, fetch_press_by_id, insert_press
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

@app.get("/static/default.png")
async def default_image():
    return FileResponse("static/default.png")

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
  description_prompt = "あなたは与えられたxの投稿内容を基に、PR TIMES用のプレスリリース文章を作成するアシスタントです。以下の構成に従って文章を作成してください：イントロ（100文字）：投稿の概要を簡潔に説明する。本文（100文字×3パート）：各パートで内容を掘り下げて説明。タイトルは内容を元に適切かつ簡潔に生成し、イントロやまとめなどの直接的な表現は避けること。タイトルの例は以下の通り、イントロのパートに対しては、【ベルギーの障害を持つアーティストと協業します！】など。まとめ（100文字）：全体の要約や今後の展望を記載する。注意事項：各段落の冒頭に【構成のタイトル】を記載すること。生成結果はplain text形式のみで出力し、装飾やマークダウン記法は使用しないでください。以上のフォーマットを守り、正確かつ魅力的なプレスリリースを作成してください。"

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
        resource.image.extend(image_urls)
      except KeyError:
          print("Error: Could not find 'text' in the response. The API response structure might have changed.")
          print(json.dumps(tweet_data, indent=4)) #Show the response for debugging
          return None
    else:
        print("Failed to retrieve tweet.")
        return None
  else:
    description_input = resource.description
  if not resource.title:
    title_input = generate_press_input("日本語で一文で以下の記事にタイトルをお付けください" + description_input)
  else:
    title_input = resource.title

  press = {
    "title": title_input,
    "description": description_input,
    "uid": resource.uid,
    "sns_url": resource.sns_url,
    "image": resource.image
  }
  
  inserted_id = insert_press(press)
  press["_id"] = inserted_id

  return JSONResponse(content=press, status_code=status.HTTP_201_CREATED)
