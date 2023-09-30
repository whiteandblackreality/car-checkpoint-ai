from typing import List, Optional

from fastapi import APIRouter, Depends, status, HTTPException

from app.schemas.schemas import *
from app.services.cameras_service import CamerasService


CamerasRouter = APIRouter(
    prefix="/v1/cameras", tags=["cameras"]
)


@CamerasRouter.get("/", response_model=List[CameraResponse])
def index(
    pageSize: Optional[int] = 100,
    startIndex: Optional[int] = 0,
    cameras_service: CamerasService = Depends(),
):
    return [
        camera.normalize()
        for camera in cameras_service.list(
            pageSize, startIndex
        )
    ]


@CamerasRouter.get("/{id}", response_model=CameraResponse)
def get(id: int, cameras_service: CamerasService = Depends()):
    try:
        return cameras_service.get(id).normalize()
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"Camera with ID {id} is not found")


@CamerasRouter.post(
    "/",
    response_model=CameraResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    camera: CameraPayload,
    cameras_service: CamerasService = Depends(),
):
    return cameras_service.create(camera).normalize()


@CamerasRouter.patch("/{id}", response_model=CameraResponse)
def update(
    id: int,
    camera: CameraPayload,
    cameras_service: CamerasService = Depends(),
):
    return cameras_service.update(id, camera).normalize()


@CamerasRouter.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete(
    id: int, cameras_service: CamerasService = Depends()
):
    return cameras_service.delete(id)
