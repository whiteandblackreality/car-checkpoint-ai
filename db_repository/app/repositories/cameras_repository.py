from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session, lazyload

from configs.db import (
    get_db_connection,
)
from models.models import Cameras


class CamerasRepository:
    db: Session

    def __init__(
        self, db: Session = Depends(get_db_connection)
    ) -> None:
        self.db = db

    def list(
        self,
        limit: Optional[int],
        start: Optional[int],
    ) -> List[Cameras]:
        query = self.db.query(Cameras)
        return query.offset(start).limit(limit).all()

    def get(self, camera: Cameras) -> Cameras:
        return self.db.get(
            Cameras,
            camera.id,
        )

    def create(self, camera: Cameras) -> Cameras:
        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)
        return camera

    def update(self, id: int, camera: Cameras) -> Cameras:
        camera.id = id
        self.db.merge(camera)
        self.db.commit()
        return camera

    def delete(self, camera: Cameras) -> None:
        self.db.delete(camera)
        self.db.commit()
        self.db.flush()
