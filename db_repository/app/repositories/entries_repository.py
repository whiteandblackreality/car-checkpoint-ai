from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session, lazyload

from app.configs.db import (
    get_db_connection,
)
from app.models.models import Entries


class EntriesRepository:
    db: Session

    def __init__(
        self, db: Session = Depends(get_db_connection)
    ) -> None:
        self.db = db

    def list(
        self,
        limit: Optional[int],
        start: Optional[int],
    ) -> List[Entries]:
        query = self.db.query(Entries)
        return query.offset(start).limit(limit).all()

    def get(self, entry: Entries) -> Entries:
        return self.db.get(
            Entries,
            entry.id,
        )

    def create(self, entry: Entries) -> Entries:
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def update(self, id: int, entry: Entries) -> Entries:
        entry.id = id
        self.db.merge(entry)
        self.db.commit()
        return entry

    def delete(self, entry: Entries) -> None:
        self.db.delete(entry)
        self.db.commit()
        self.db.flush()
