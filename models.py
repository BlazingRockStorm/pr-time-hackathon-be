from pydantic import BaseModel
from typing import List, Dict

class PressRelease(BaseModel):
  title: str
  description: str
  sns_url: str
  uid: str
  image: list
    