from typing import List, Optional

from fastapi import Depends
from app.models.models import Frames

from app.repositories.frames_repository import FramesRepository
from app.schemas.schemas import FramePayload


class FramesService:
    frames_repository: FramesRepository

    def __init__(
        self, frames_repository: FramesRepository = Depends()
    ) -> None:
        self.frames_repository = frames_repository

    def create(self, frame_body: FramePayload) -> Frames:
        return self.frames_repository.create(
            Frames(base64_frame=frame_body.base64_frame,
                   video_id=frame_body.video_id,
                   car_number=frame_body.car_number,
                   car_model=frame_body.car_model,)
        )

    def get(self, frame_id: int) -> Frames:
        return self.frames_repository.get(
            Frames(id=frame_id)
        )

    def list(
        self,
        pageSize: Optional[int] = 100,
        startIndex: Optional[int] = 0,
    ) -> List[Frames]:
        return self.frames_repository.list(
            pageSize, startIndex
        )

    def update(
        self, frame_id: int, frame_body: FramePayload
    ) -> Frames:
        return self.frames_repository.update(
            frame_id, Frames(base64_frame=frame_body.base64_frame,
                             video_id=frame_body.video_id,
                             car_number=frame_body.car_number,
                             car_model=frame_body.car_model,)
        )
