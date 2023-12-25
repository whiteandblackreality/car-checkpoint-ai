import shutil
import random
from typing import List

from fastapi import APIRouter, Depends, status, File, UploadFile

from app.schemas.schemas import *
from app.configs.storage import VIDEOS_STORAGE
from app.configs import get_random_string
from app.repositories.videos_repository import VideosRepository


VideosRouter = APIRouter(
    prefix="/v1/videos", tags=["car-checkpoint-ai"]
)


@VideosRouter.post(
    "/",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    videofile: UploadFile,
    videos_repository: VideosRepository = Depends(),
):
    name = get_random_string(20)
    with open(f"{VIDEOS_STORAGE.get_path()}/{name}.mp4", "wb") as buffer:
        shutil.copyfileobj(videofile.file, buffer)
    return videos_repository.create(f"{VIDEOS_STORAGE.get_path()}/{name}.mp4")


@VideosRouter.get("/get_answers/{video_id}", response_model=List[FrameResponse])
def get(video_id: int, videos_repository: VideosRepository = Depends()):
    try:
        return videos_repository.get_answers(video_id)
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} is not found")
