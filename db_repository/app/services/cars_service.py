from typing import List, Optional

from fastapi import Depends
from models.models import Cars

from repositories.cars_repository import CarsRepository
from schemas.schemas import CarPayload


class CarsService:
    cars_repository: CarsRepository

    def __init__(
        self, cars_repository: CarsRepository = Depends()
    ) -> None:
        self.cars_repository = cars_repository

    def create(self, car_body: CarPayload) -> Cars:
        return self.cars_repository.create(
            Cars(label=car_body.label,
                 model=car_body.model,
                 generation=car_body.generation,
                 color=car_body.color,
                 number=car_body.number,)
        )

    def delete(self, car_id: int) -> None:
        return self.cars_repository.delete(
            Cars(id=car_id)
        )

    def get(self, car_id: int) -> Cars:
        return self.cars_repository.get(
            Cars(id=car_id)
        )

    def list(
        self,
        pageSize: Optional[int] = 100,
        startIndex: Optional[int] = 0,
    ) -> List[Cars]:
        return self.cars_repository.list(
            pageSize, startIndex
        )

    def update(
        self, car_id: int, car_body: CarPayload
    ) -> Cars:
        return self.cars_repository.update(
            car_id, Cars(label=car_body.label,
                         model=car_body.model,
                         generation=car_body.generation,
                         color=car_body.color,
                         number=car_body.number,))
