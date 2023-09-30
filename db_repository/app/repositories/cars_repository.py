from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session, lazyload

from app.configs.db import (
    get_db_connection,
)
from app.models.models import Cars


class CarsRepository:
    db: Session

    def __init__(
        self, db: Session = Depends(get_db_connection)
    ) -> None:
        self.db = db

    def list(
        self,
        limit: Optional[int],
        start: Optional[int],
    ) -> List[Cars]:
        query = self.db.query(Cars)
        return query.offset(start).limit(limit).all()

    def get(self, car: Cars) -> Cars:
        return self.db.get(
            Cars,
            car.id,
        )

    def create(self, car: Cars) -> Cars:
        self.db.add(car)
        self.db.commit()
        self.db.refresh(car)
        return car

    def update(self, id: int, car: Cars) -> Cars:
        car.id = id
        self.db.merge(car)
        self.db.commit()
        return car

    def delete(self, car: Cars) -> None:
        self.db.delete(car)
        self.db.commit()
        self.db.flush()
