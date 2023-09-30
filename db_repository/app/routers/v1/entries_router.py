from typing import List, Optional

from fastapi import APIRouter, Depends, status, HTTPException

from app.schemas.schemas import *
from app.services.entries_service import EntriesService


EntriesRouter = APIRouter(
    prefix="/v1/entries", tags=["entries"]
)


@EntriesRouter.get("/", response_model=List[EntryResponse])
def index(
    pageSize: Optional[int] = 100,
    startIndex: Optional[int] = 0,
    entries_service: EntriesService = Depends(),
):
    return [
        entry.normalize()
        for entry in entries_service.list(
            pageSize, startIndex
        )
    ]


@EntriesRouter.get("/{id}", response_model=EntryResponse)
def get(id: int, entries_service: EntriesService = Depends()):
    try:
        return entries_service.get(id).normalize()
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"Entry with ID {id} is not found")


@EntriesRouter.post(
    "/",
    response_model=EntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    entry: EntryPayload,
    entries_service: EntriesService = Depends(),
):
    return entries_service.create(entry).normalize()


@EntriesRouter.patch("/{id}", response_model=EntryResponse)
def update(
    id: int,
    entry: EntryPayload,
    entries_service: EntriesService = Depends(),
):
    return entries_service.update(id, entry).normalize()


@EntriesRouter.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete(
    id: int, entries_service: EntriesService = Depends()
):
    return entries_service.delete(id)
