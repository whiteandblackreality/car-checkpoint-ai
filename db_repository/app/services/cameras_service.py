from typing import List, Optional

from fastapi import Depends
from models.models import Cameras

from repositories.cameras_repository import CamerasRepository
from schemas.schemas import CameraPayload


class CamerasService:
    cameras_repository: CamerasRepository

    def __init__(
        self, cameras_repository: CamerasRepository = Depends()
    ) -> None:
        self.cameras_repository = cameras_repository

    def create(self, camera_body: CameraPayload) -> Cameras:
        return self.cameras_repository.create(
            Cameras(place=camera_body.place,
                    about=camera_body.about,
                    link=camera_body.link,)
        )

    def delete(self, camera_id: int) -> None:
        return self.cameras_repository.delete(
            Cameras(id=camera_id)
        )

    def get(self, camera_id: int) -> Cameras:
        return self.cameras_repository.get(
            Cameras(id=camera_id)
        )

    def list(
        self,
        pageSize: Optional[int] = 100,
        startIndex: Optional[int] = 0,
    ) -> List[Cameras]:
        return self.cameras_repository.list(
            pageSize, startIndex
        )

    def update(
        self, camera_id: int, camera_body: CameraPayload
    ) -> Cameras:
        return self.cameras_repository.update(
            camera_id, Cameras(place=camera_body.place,
                               about=camera_body.about,
                               link=camera_body.link,))
