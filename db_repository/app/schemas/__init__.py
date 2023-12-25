from typing import Optional
from pydantic import BaseModel


class FrameBase(BaseModel):
    base64_frame: Optional[str]
    video_id: Optional[int]
    car_number: Optional[str]
    car_model: Optional[str]

    class Config:
        orm_mode = True


class VideoBase(BaseModel):
    video_path: Optional[str]

    class Config:
        orm_mode = True
