from typing import List, Optional

from fastapi import APIRouter, Depends, status, HTTPException

from app.schemas.schemas import *
from app.services.videos_service import VideosService


VideosRouter = APIRouter(
    prefix="/v1/videos", tags=["videos"]
)


@VideosRouter.get("/", response_model=List[VideoResponse])
def index(
    pageSize: Optional[int] = 100,
    startIndex: Optional[int] = 0,
    videos_service: VideosService = Depends(),
):
    return [
        video.normalize()
        for video in videos_service.list(
            pageSize, startIndex
        )
    ]


@VideosRouter.get("/{id}", response_model=VideoResponse)
def get(id: int, videos_service: VideosService = Depends()):
    try:
        return videos_service.get(id).normalize()
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"Video with ID {id} is not found")


@VideosRouter.post(
    "/",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    video: VideoPayload,
    videos_service: VideosService = Depends(),
):
    return videos_service.create(video).normalize()


@VideosRouter.patch("/{id}", response_model=VideoResponse)
def update(
    id: int,
    video: VideoPayload,
    videos_service: VideosService = Depends(),
):
    return videos_service.update(id, video).normalize()


@VideosRouter.get("frames_by_video_id/{id}", response_model=List[FrameResponse])
def get(id: int, videos_service: VideosService = Depends()):
    try:
        return [frame.normalize() for frame in videos_service.get_frames_by_video_id(id)]
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"Video with ID {id} is not found")
