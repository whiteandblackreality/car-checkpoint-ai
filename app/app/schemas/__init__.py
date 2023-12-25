from typing import Optional
from pydantic import BaseModel


class VideoBase(BaseModel):
    video_path: Optional[str]

    class Config:
        orm_mode = True
