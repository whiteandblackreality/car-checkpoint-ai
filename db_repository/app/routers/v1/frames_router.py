from typing import List, Optional

from fastapi import APIRouter, Depends, status, HTTPException

from app.schemas.schemas import *
from app.services.frames_service import FramesService


FramesRouter = APIRouter(
    prefix="/v1/frames", tags=["frames"]
)


@FramesRouter.get("/", response_model=List[FrameResponse])
def index(
    pageSize: Optional[int] = 100,
    startIndex: Optional[int] = 0,
    frames_service: FramesService = Depends(),
):
    return [
        frame.normalize()
        for frame in frames_service.list(
            pageSize, startIndex
        )
    ]


@FramesRouter.get("/{id}", response_model=FrameResponse)
def get(id: int, frames_service: FramesService = Depends()):
    try:
        return frames_service.get(id).normalize()
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"Frame with ID {id} is not found")


@FramesRouter.post(
    "/",
    response_model=FrameResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    frame: FramePayload,
    frames_service: FramesService = Depends(),
):
    return frames_service.create(frame).normalize()
