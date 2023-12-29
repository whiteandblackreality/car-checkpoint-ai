from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, BOOLEAN
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models import EntityMeta


class Videos(EntityMeta):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    video_path = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    frames = relationship('Frames', back_populates="videos")

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "video_path": self.video_path.__str__(),
            "created_at": self.created_at.__str__(),
        }


class Frames(EntityMeta):
    __tablename__ = "frames"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    base64_frame = Column(String, nullable=False)
    video_id = Column(Integer, ForeignKey('videos.id'),  nullable=False)
    car_number = Column(String, nullable=True)
    car_model = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    videos = relationship('Videos', back_populates="frames")

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "base64_frame": self.base64_frame.__str__(),
            "video_id": self.video_id.__str__(),
            "car_number": self.car_number.__str__(),
            "car_model": self.car_model.__str__(),
            "created_at": self.created_at.__str__(),
        }
