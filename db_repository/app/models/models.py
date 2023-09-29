from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, BOOLEAN
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models import EntityMeta


class Cars(EntityMeta):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    label = Column(String, nullable=True)
    model = Column(String, nullable=True)
    generation = Column(Integer, nullable=True)
    color = Column(String, nullable=True)
    number = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    entries = relationship('Entries', back_populates="cars")

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "label": self.label.__str__(),
            "model": self.model,
            "generation": self.generation.__str__(),
            "color": self.color.__str__(),
            "number": self.number.__str__(),
            "created_at": self.created_at.__str__(),
        }


class Entries(EntityMeta):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=True)
    fixation_s3_link = Column(String, nullable=False)
    camera_id = Column(Integer, ForeignKey('cameras.id'),  nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    cars = relationship('Cars', back_populates="entries")
    cameras = relationship('Cameras', back_populates="entries")

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "car_id": self.car_id.__str__(),
            "fixation_s3_link": self.fixation_s3_link.__str__(),
            "camera_id": self.camera_id.__str__(),
            "type": self.type.__str__(),
            "created_at": self.created_at.__str__(),
        }


class Cameras(EntityMeta):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    place = Column(String, nullable=False)
    about = Column(String, nullable=True)
    link = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    entries = relationship('Entries', back_populates="cameras")

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "place": self.place.__str__(),
            "about": self.about.__str__(),
            "created_at": self.created_at.__str__(),
        }
