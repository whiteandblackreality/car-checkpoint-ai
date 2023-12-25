from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session, lazyload

from app.configs.storage import (
    get_storage_connection, VideosStorage
)
from app.schemas.schemas import VideoPayload, VideoResponse, FrameResponse


class VideosRepository:
    storage: VideosStorage

    def __init__(
        self, storage: Session = Depends(get_storage_connection)
    ) -> None:
        self.storage = storage

    def create(self, video_path: str ) -> VideoResponse:
        return self.storage.create_video_in_db(video_path)

    def get_answers(self, video_id: int) -> List[FrameResponse]:
        return self.storage.get_frames(video_id)
