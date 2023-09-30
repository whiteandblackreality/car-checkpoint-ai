from typing import List, Optional

from fastapi import Depends
from models.models import Entries

from repositories.entries_repository import EntriesRepository
from schemas.schemas import EntryPayload


class EntriesService:
    entries_repository: EntriesRepository

    def __init__(
        self, entries_repository: EntriesRepository = Depends()
    ) -> None:
        self.entries_repository = entries_repository

    def create(self, entry_body: EntryPayload) -> Entries:
        return self.entries_repository.create(
            Entries(car_id=entry_body.car_id,
                    car_fixation_s3_linkid=entry_body.fixation_s3_link,
                    camera_id=entry_body.camera_id,
                    type=entry_body.type,)
        )

    def delete(self, entry_id: int) -> None:
        return self.entries_repository.delete(
            Entries(id=entry_id)
        )

    def get(self, entry_id: int) -> Entries:
        return self.entries_repository.get(
            Entries(id=entry_id)
        )

    def list(
        self,
        pageSize: Optional[int] = 100,
        startIndex: Optional[int] = 0,
    ) -> List[Entries]:
        return self.entries_repository.list(
            pageSize, startIndex
        )

    def update(
        self, entry_id: int, entry_body: EntryPayload
    ) -> Entries:
        return self.entries_repository.update(
            entry_id, Entries(car_id=entry_body.car_id,
                              car_fixation_s3_linkid=entry_body.fixation_s3_link,
                              camera_id=entry_body.camera_id,
                              type=entry_body.type,))
