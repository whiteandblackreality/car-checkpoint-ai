from app.schemas import CarBase, EntryBase, CameraBase


class CarPayload(CarBase):
    pass


class CarResponse(CarBase):
    id: int


class EntryPayload(EntryBase):
    pass


class EntryResponse(EntryBase):
    id: int


class CameraPayload(CameraBase):
    pass


class CameraResponse(CameraBase):
    id: int
