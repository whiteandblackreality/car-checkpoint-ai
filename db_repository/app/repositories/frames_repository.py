from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session, lazyload

from app.configs.db import (
    get_db_connection,
)
from app.models.models import Frames
from app.repositories import decorator_rollback_error


class FramesRepository:
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
    ) -> List[Frames]:
        query = self.db.query(Frames)
        return query.offset(start).limit(limit).all()

    def get(self, frame: Frames) -> Frames:
        return self.db.get(
            Frames,
            frame.id,
        )

    @decorator_rollback_error
    def create(self, frame: Frames) -> Frames:
        self.db.add(frame)
        self.db.commit()
        self.db.refresh(frame)
        return frame

    @decorator_rollback_error
    def update(self, id: int, frame: Frames) -> Frames:
        frame.id = id
        self.db.merge(frame)
        self.db.commit()
        return frame

    @decorator_rollback_error
    def delete(self, frame: Frames) -> None:
        self.db.delete(frame)
        self.db.commit()
        self.db.flush()
