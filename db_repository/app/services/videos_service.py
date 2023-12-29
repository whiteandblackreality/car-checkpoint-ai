from typing import List, Optional

from fastapi import Depends
from app.models.models import Videos, Frames

from app.repositories.videos_repository import VideosRepository
from app.schemas.schemas import VideoPayload


class VideosService:
    videos_repository: VideosRepository

    def __init__(
        self, videos_repository: VideosRepository = Depends()
    ) -> None:
        self.videos_repository = videos_repository

    def create(self, video_body: VideoPayload) -> Videos:
        return self.videos_repository.create(
            Videos(video_path=video_body.video_path,)
        )

    def get(self, video_id: int) -> Videos:
        return self.videos_repository.get(
            Videos(id=video_id)
        )

    def list(
        self,
        pageSize: Optional[int] = 100,
        startIndex: Optional[int] = 0,
    ) -> List[Videos]:
        return self.videos_repository.list(
            pageSize, startIndex
        )

    def update(
        self, video_id: int, video_body: VideoPayload
    ) -> Videos:
        return self.videos_repository.update(
            video_id, Videos(video_path=video_body.place,)
        )

    def get_frames_by_video_id(
            self, video_id: int
    ) -> List[Frames]:
        return self.videos_repository.get(
            Videos(id=video_id)
        ).frames
