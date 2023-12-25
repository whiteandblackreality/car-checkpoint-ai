from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session, lazyload

from app.configs.db import (
    get_db_connection,
)
from app.models.models import Videos
from app.repositories import decorator_rollback_error


class VideosRepository:
    db: Session

    def __init__(
        self, db: Session = Depends(get_db_connection)
    ) -> None:
        self.db = db

    @decorator_rollback_error
    def list(
        self,
        limit: Optional[int],
        start: Optional[int],
    ) -> List[Videos]:
        query = self.db.query(Videos)
        return query.offset(start).limit(limit).all()

    @decorator_rollback_error
    def get(self, video: Videos) -> Videos:
        return self.db.get(
            Videos,
            video.id,
        )

    @decorator_rollback_error
    def create(self, video: Videos) -> Videos:
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    @decorator_rollback_error
    def update(self, id: int, video: Videos) -> Videos:
        video.id = id
        self.db.merge(video)
        self.db.commit()
        return video

    @decorator_rollback_error
    def delete(self, video: Videos) -> None:
        self.db.delete(video)
        self.db.commit()
        self.db.flush()
