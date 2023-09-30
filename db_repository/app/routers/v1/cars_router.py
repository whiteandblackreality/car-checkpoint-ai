from typing import List, Optional

from fastapi import APIRouter, Depends, status, HTTPException

from schemas.schemas import *
from services.cars_service import CarsService


CarsRouter = APIRouter(
    prefix="/v1/cars", tags=["cars"]
)


@CarsRouter.get("/", response_model=List[CarResponse])
def index(
    pageSize: Optional[int] = 100,
    startIndex: Optional[int] = 0,
    cars_service: CarsService = Depends(),
):
    return [
        car.normalize()
        for car in cars_service.list(
            pageSize, startIndex
        )
    ]


@CarsRouter.get("/{id}", response_model=CarResponse)
def get(id: int, cars_service: CarsService = Depends()):
    try:
        return cars_service.get(id).normalize()
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"Car with ID {id} is not found")


@CarsRouter.post(
    "/",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    car: CarPayload,
    cars_service: CarsService = Depends(),
):
    return cars_service.create(car).normalize()


@CarsRouter.patch("/{id}", response_model=CarResponse)
def update(
    id: int,
    car: CarPayload,
    cars_service: CarsService = Depends(),
):
    return cars_service.update(id, car).normalize()


@CarsRouter.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete(
    id: int, cars_service: CarsService = Depends()
):
    return cars_service.delete(id)
