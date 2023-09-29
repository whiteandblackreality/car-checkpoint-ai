from typing import Optional
from pydantic import BaseModel


class CarBase(BaseModel):
    label: Optional[str]
    model: Optional[str]
    generation: Optional[int]
    color: Optional[str]
    number: Optional[str]

    class Config:
        orm_mode = True


class EntryBase(BaseModel):
    car_id: Optional[int]
    fixation_s3_link: str
    camera_id: int
    type: str

    class Config:
        orm_mode = True


class CameraBase(BaseModel):
    place: str
    about: Optional[str]
    link: str

    class Config:
        orm_mode = True
